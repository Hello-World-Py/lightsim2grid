# Copyright (c) 2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of LightSim2grid, LightSim2grid implements a c++ backend targeting the Grid2Op platform.

"""
Use the pandapower converter to properly initialized a GridModel c++ object.
"""

import numpy as np
from lightsim2grid_cpp import GridModel, PandaPowerConverter


def init(pp_net):
    """
    Convert a pandapower network as input into a GridModel.

    This does not throw any error at the moment when the conversion is not possible.

    Cases for which conversion is not possible include, but are not limited to:

    - the pandapower grid has 3 winding transformers
    - the pandapower grid has xwards
    - the pandapower grid any parrallel "elements" (at least one of the column "parrallel" is not 1)
    - some `g_us_per_km` for some lines are not zero
    - some `p_mw` for some shunts are not zero
    - some `tap_step_degre` are non zero for some trafo
    - no "ext_grid" is reported on the initial grid

    if you really need any of the above, please submit a github issue and we will work on their support.

    This conversion has been extensively studied for the case118() of pandapower.networks and should work
    really well for this grid. Actually, this grid is used for testing the GridModel class.

    Parameters
    ----------
    pp_net: :class:`pandapower.grid`
        The initial pandapower network you want to convert

    Returns
    -------
    model: :class:`GridModel`
        The initialize gridmodel

    """
    # initialize and use converters
    converter = PandaPowerConverter()
    converter.set_sn_mva(pp_net.sn_mva)  # TODO raise an error if not set !
    converter.set_f_hz(pp_net.f_hz)
    line_r, line_x, line_h = \
        converter.get_line_param(
            pp_net.line["r_ohm_per_km"].values * pp_net.line["length_km"].values,
            pp_net.line["x_ohm_per_km"].values * pp_net.line["length_km"].values,
            pp_net.line["c_nf_per_km"].values * pp_net.line["length_km"].values,
            pp_net.line["g_us_per_km"].values * pp_net.line["length_km"].values,
            pp_net.bus.loc[pp_net.line["from_bus"]]["vn_kv"],
            pp_net.bus.loc[pp_net.line["to_bus"]]["vn_kv"]
        )
    trafo_r, trafo_x, trafo_b = \
        converter.get_trafo_param(pp_net.trafo["vn_hv_kv"].values,
                                  pp_net.trafo["vn_lv_kv"].values,
                                  pp_net.trafo["vk_percent"].values,
                                  pp_net.trafo["vkr_percent"].values,
                                  pp_net.trafo["sn_mva"].values,
                                  pp_net.trafo["pfe_kw"].values,
                                  pp_net.trafo["i0_percent"].values,
                                  pp_net.bus.loc[pp_net.trafo["lv_bus"]]["vn_kv"]
                                       )

    # set up the data model accordingly
    model = GridModel()
    tmp_bus_ind = np.argsort(pp_net.bus.index)
    model.init_bus(pp_net.bus.iloc[tmp_bus_ind]["vn_kv"].values,
                   pp_net.line.shape[0],
                   pp_net.trafo.shape[0])

    model.init_powerlines(line_r, line_x, line_h,
                          pp_net.line["from_bus"].values,
                          pp_net.line["to_bus"].values
                               )
    for line_id, sh_status in enumerate(pp_net.line["in_service"].values):
        if not sh_status:
            # powerline is deactivated
            model.deactivate_powerline(line_id)

    # init the shunts
    model.init_shunt(pp_net.shunt["p_mw"].values,
                     pp_net.shunt["q_mvar"].values,
                     pp_net.shunt["bus"].values
                     )
    for sh_id, sh_status in enumerate(pp_net.shunt["in_service"].values):
        if not sh_status:
            # shunt is deactivated
            model.deactivate_shunt(sh_id)

    # handle the trafos
    tap_step_pct = pp_net.trafo["tap_step_percent"].values
    tap_step_pct[~np.isfinite(tap_step_pct)] = 0.

    tap_pos = pp_net.trafo["tap_pos"].values
    tap_pos[~np.isfinite(tap_pos)] = 0.

    is_tap_hv_side = pp_net.trafo["tap_side"].values == "hv"
    is_tap_hv_side[~np.isfinite(tap_pos)] = True
    model.init_trafo(trafo_r,
                     trafo_x,
                     trafo_b,
                     tap_step_pct,
                     tap_pos,
                     is_tap_hv_side,
                     pp_net.trafo["hv_bus"].values,
                     pp_net.trafo["lv_bus"].values)
    for tr_id, sh_status in enumerate(pp_net.trafo["in_service"].values):
        if not sh_status:
            # trafo is deactivated
            model.deactivate_trafo(tr_id)

    # handle loads
    model.init_loads(pp_net.load["p_mw"].values,
                     pp_net.load["q_mvar"].values,
                     pp_net.load["bus"].values
                          )
    for load_id, sh_status in enumerate(pp_net.load["in_service"].values):
        if not sh_status:
            # load is deactivated
            model.deactivate_load(load_id)

    # handle generators
    model.init_generators(pp_net.gen["p_mw"].values,
                          pp_net.gen["vm_pu"].values,
                          pp_net.gen["min_q_mvar"].values,
                          pp_net.gen["max_q_mvar"].values,
                          pp_net.gen["bus"].values
                          )
    for gen_id, sh_status in enumerate(pp_net.gen["in_service"].values):
        if not sh_status:
            # generator is deactivated
            model.deactivate_gen(gen_id)

    # deal with slack bus
    # TODO handle that better maybe, and warn only one slack bus is implemented
    if np.any(pp_net.gen["slack"].values):
        slack_gen_id = np.where(pp_net.gen["slack"].values)[0]
        model.change_v_gen(slack_gen_id, pp_net.gen["vm_pu"][slack_gen_id])
    else:
        # there is no slack bus in the generator of the pp grid

        # first i try to see if a generator is connected to a slack bus
        slack_bus_id = pp_net.ext_grid["bus"].values[0]
        if np.any(pp_net.gen["bus"].values == slack_bus_id):
            slack_gen_id = np.where(pp_net.gen["bus"].values == slack_bus_id)[0]
        else:
            # no gen is connected to a slack bus, so i create one.
            gen_p = np.concatenate((pp_net.gen["p_mw"].values, [np.sum(pp_net.load["p_mw"]) - np.sum(pp_net.gen["p_mw"])]))
            gen_v = np.concatenate((pp_net.gen["vm_pu"].values, [pp_net.ext_grid["vm_pu"].values[0]]))
            gen_bus = np.concatenate((pp_net.gen["bus"].values, [slack_bus_id]))
            gen_min_q = np.concatenate((pp_net.gen["min_q_mvar"].values, [-999999.]))
            gen_max_q = np.concatenate((pp_net.gen["max_q_mvar"].values, [+99999.]))
            model.init_generators(gen_p, gen_v, gen_min_q, gen_max_q, gen_bus)
            slack_gen_id = pp_net.gen["bus"].shape[0]

    model.add_gen_slackbus(slack_gen_id)
    return model