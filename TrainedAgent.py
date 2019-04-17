__author__ = 'Tony Beltramelli - www.tonybeltramelli.com'

import sys
import numpy as np

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

from End2EndWeightSharingModel import End2EndWeightSharingModel
from Utils import Utils

np.random.seed(1234)

MAP = sys.argv[sys.argv.index('--map') + 1]

AGENT = {
    'MoveToBeacon': 'agent_beacon',
    'CollectMineralShards': 'agent_mineral'
}[MAP]


class TrainedAgent(base_agent.BaseAgent):
    def __init__(self):
        base_agent.BaseAgent.__init__(self)

        self.model = End2EndWeightSharingModel()
        self.model.load(AGENT)

    def step(self, obs):
        super(TrainedAgent, self).step(obs)

        observation = obs.observation.feature_minimap[5]
        observation = Utils.feature_array_to_img(observation, max_target_value=1.0)
        observation = Utils.resize_squared_img(observation, 84)
        #Utils.show(observation)

        output_size = len(actions.FUNCTIONS)

        available_actions = np.zeros(output_size)
        for action_index in obs.observation.available_actions:
            available_actions[action_index] = 1.0

        input_batch = [np.array([observation]), np.array([available_actions])]
        action, position = self.model.predict(input_batch)
        screen_size = np.shape(obs.observation.feature_screen)[1]
        x = int(screen_size * position[0])
        y = int(screen_size * position[1])

        if action in obs.observation.available_actions:
            print("action is available: ", action, x, y)
        else:
            action = np.random.choice(obs.observation.available_actions)
            print("take random action")

        if action == actions.FUNCTIONS.no_op.id:
            params = []
        elif action == actions.FUNCTIONS.Move_screen.id:
            params = [[0], [x, y]]
        elif action == actions.FUNCTIONS.select_army.id:
            params = [[0]]
        else:
            params = [[np.random.randint(0, size) for size in arg.sizes] for arg in self.action_spec.functions[action].args]

        return actions.FunctionCall(action, params)
