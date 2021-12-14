from aiogram.utils.helper import Helper, HelperMode, ListItem


class TestStates(Helper):
    mode = HelperMode.snake_case

    TEST_STATE_START = ListItem()
    TEST_STATE_OTHER = ListItem()
    TEST_STATE_OTHER_NAME = ListItem()
    TEST_STATE_OTHER_CAR = ListItem()
    TEST_STATE_PROBLEM = ListItem()
    TEST_STATE_PROBLEM_ADDRESS = ListItem()