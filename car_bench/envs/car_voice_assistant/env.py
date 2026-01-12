# Copyright Sierra

from typing import Optional, Union

from car_bench.envs.base import Env
from car_bench.envs.car_voice_assistant.mock_data import load_data
from car_bench.envs.car_voice_assistant.tools import (
    ALL_TOOLS,
)
from car_bench.envs.car_voice_assistant.wiki import WIKI
from car_bench.envs.policy_evaluator import PolicyEvaluatorStrategy
from car_bench.envs.user.user import UserStrategy


class MockCarVoiceAssistantDomainEnv(Env):
    def __init__(
        self,
        user_strategy: Union[str, UserStrategy] = UserStrategy.LLM,
        policy_evaluator_strategy: Union[
            str, UserStrategy
        ] = PolicyEvaluatorStrategy.LLM,
        user_model: str = "gpt-4.1-mini",
        policy_evaluator_model: str = "gpt-4.1-mini",
        user_provider: Optional[str] = None,
        policy_evaluator_provider: Optional[str] = None,
        user_thinking: bool = False,
        task_split: str = "test",
        task_index: Optional[int] = None,
        evaluate_policy: Optional[bool] = False,
        score_tool_execution_errors: Optional[bool] = False,
        score_policy_errors: Optional[bool] = False,
        use_user_as_a_tool_tools: bool = False,
    ):
        match task_split:
            case "test":
                from car_bench.envs.car_voice_assistant.tasks.tasks_test import (
                    TASKS_TEST as tasks,
                )
            case "train":
                from car_bench.envs.car_voice_assistant.tasks.tasks_train import (
                    TASKS_TRAIN as tasks,
                )
            case "dev":
                from car_bench.envs.car_voice_assistant.tasks.tasks_dev import (
                    TASKS as tasks,
                )
            case "base":
                from car_bench.envs.car_voice_assistant.tasks.tasks_base import (
                    TASKS as tasks,
                )
            case "hallucination":
                from car_bench.envs.car_voice_assistant.tasks.tasks_hallucination import (
                    TASKS as tasks,
                )
            case "disambiguation":
                from car_bench.envs.car_voice_assistant.tasks.tasks_disambiguation import (
                    TASKS as tasks,
                )

            case _:
                raise ValueError(f"Unknown task split: {task_split}")

        all_tools_plus_user_as_a_tool = None
        wiki_with_user_as_a_tool = None
        if use_user_as_a_tool_tools:
            all_tools_plus_user_as_a_tool = ALL_TOOLS_PLUS_USER_AS_A_TOOL
            wiki_with_user_as_a_tool = WIKI

        super().__init__(
            data_load_func=load_data,
            tools=all_tools_plus_user_as_a_tool or ALL_TOOLS,
            tasks=tasks,
            wiki=wiki_with_user_as_a_tool or WIKI,
            user_strategy=user_strategy,
            user_model=user_model,
            user_thinking=user_thinking,
            policy_evaluator_strategy=policy_evaluator_strategy,
            policy_evaluator_model=policy_evaluator_model,
            user_provider=user_provider,
            policy_evaluator_provider=policy_evaluator_provider,
            task_index=task_index,
            evaluate_policy=evaluate_policy,
            score_tool_execution_errors=score_tool_execution_errors,
            score_policy_errors=score_policy_errors,
        )
        self.terminate_tools = ["call_phone_by_number"]
