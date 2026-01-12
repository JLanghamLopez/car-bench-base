# CAR-bench: Evaluating the Consistency and Limit-Awareness of LLM Agents under Real-World Uncertainty

## Setup

1. Clone this repository
2. Install from source (which also installs required packages):

```bash
pip install -e .
```

3. Set up your OpenAI / Anthropic / Google / Mistral / AnyScale API keys as environment variables.

```bash
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY =...
```

4. Unfortunately, due to file size limit in the submission, we cannot include the mock databases. They will be published with the final version. For more details on the mock data please refer to: `car_bench/envs/car_voice_assistant/mock_data/readme.md`.

## Run

Run a tool-calling agent on the base split of the in-car voice assistant environment:

```bash
python run.py --agent-strategy tool-calling --env car_voice_assistant --model claude-sonnet-4-20250514 --model-provider anthropic --user-model gemini-2.5-flash --user-model-provider gemini --user-thinking --user-strategy llm --max-concurrency 2 --task-split base --evaluate-policy --score-tool-execution-errors --score-policy-errors
```

Set max concurrency according to your API limit(s).

To run specific tasks, use the `--task-ids` flag. For example:

```bash
python run.py --agent-strategy tool-calling --env car_voice_assistant --model claude-sonnet-4-20250514 --model-provider anthropic --user-model gemini-2.5-flash --user-model-provider gemini --user-thinking --user-strategy llm --max-concurrency 2 --task-ids 2 4 6 --task-split base --evaluate-policy --score-tool-execution-errors --score-policy-errors
```

This command will run only the tasks with IDs 2, 4, and 6.

To activate reasoning in models that support it, use the `--thinking` flag, and to activate interleaved reasoning, use the `--interleaved-thinking` flag (currently only supported by Anthropic models). The reasoning effort can be set to `low`, `medium`, `high`, or a specific budget as an integer with the `--reasoning-effort` flag.

```bash
python run.py --agent-strategy tool-calling --env car_voice_assistant --model claude-sonnet-4-20250514 --model-provider anthropic --user-model gemini-2.5-flash --user-model-provider gemini --user-thinking --user-strategy llm --max-concurrency 2 --task-ids 2 4 6 --task-split base --evaluate-policy --score-tool-execution-errors --score-policy-errors --thinking --interleaved-thinking --reasoning-effort medium
```

To run the hallucination or disambiguation splits, use the `--task-split` flag with the appropriate split name.

```bash
python run.py --agent-strategy tool-calling --env car_voice_assistant --model claude-sonnet-4-20250514 --model-provider anthropic --user-model gemini-2.5-flash --user-model-provider gemini --user-thinking --user-strategy llm --max-concurrency 2 --task-split hallucination --evaluate-policy --score-tool-execution-errors --score-policy-errors
```


## User simulators

By default, we use `gemini-2.5-flash` with reasoning enabled as the user simulator. You can use other models by setting the `--user-model` flag. Similar as for the agent, you can activate reasoning in models that support it with the `--user-thinking` flag (see above run examples). 

If you want to manually test a model, you can use the `--user-strategy` flag to set the user strategy to `human`, then you can interact with the model in the terminal:

```bash
python run.py --agent-strategy tool-calling --env car_voice_assistant --model claude-sonnet-4-20250514 --model-provider anthropic --user-strategy human --max-concurrency 1 --task-ids 0 --task-split base --evaluate-policy --score-tool-execution-errors --score-policy-errors
```

## Task splits and evaluation

The `car_voice_assistant` environment has the following task splits:

- `base` (100 datapoints): The base split of the in-car voice assistant environment.
  - Evaluation of `base` datapoints:
      - `r_actions_final`: Compares the state of the car after the agent's actions with the state of the car after the ground truth actions.
      - `r_actions_intermediate`: Compares if every intermediate state reached after each agent's actions within one turn is also reached by the ground truth actions. We therefore penalize incorrect state-changing actions even though they might be corrected afterwards - this is because unexpected state changes can lead to a surprisal of the driver and with that to distraction from driving.
      - `r_tool_subset`: Compares by tool name (without parameters) if the ground truth actions are a subset of the agent's actions. This evaluates needed get tools (non-state-changing tools) are called while allowing the agent to use additional get tools.
      - `r_tool_execution_errors`: Evaluates if the agent called the tools with valid parameters (do not have to be correct by ground truth).
      - `r_policy_errors`: Evaluates if the agent's actions are compliant with the policy. Some policies rules are automatically evaluated by code, others are evaluated by LLM.
      - `r_user_end_conversation`: Always 1.0 (correct) for the base split.

- `hallucination` (90 datapoints): Augments datapoints from the `base` split by removing needed tools, tool parameters, or tool results. With this removal, the user goal is not satisfiable anymore by the agent. 
  - Evaluation of `hallucination` datapoints:
      - `r_actions_final`: Skipped.
      - `r_actions_intermediate`: Skipped.
      - `r_tool_subset`: Skipped.
      - `r_tool_execution_errors`: Included, same as for the base split.
      - `r_policy_errors`: Included, same as for the base split.
      - `r_user_end_conversation`: User has additional instructions to end the conversation: user generates `ASSISTANT_ACKNOWLEDGED_REMOVED_PART` (r=1.0) if the assistant acknowledged the missing capability or information caused by the removed part, or `HALLUCINATION_ERROR` (r=0.0) if the assistant does not acknowledge the missing capability or information, but instead hallucinates the action, ignores the intent about the removed part, or generates a different action without including the user.

- `disambiguation` (50 datapoints): Augments datapoints from the `base` split by adding ambiguities to the user instructions that either have to be resolved with the user or can be resolved internally by the assistant (through stored user preferences, policy rules, context state). The assistant has a clear disambiguation policy: every ambiguity should first be resolved internally, if after internal disambiguation more than one singular valid option is left, then the user has to be included to resolve the ambiguity.
  - Evaluation of `disambiguation` datapoints:
      - `r_actions_final`: Included, same as for the base split.
      - `r_actions_intermediate`: Included, same as for the base split.
      - `r_tool_subset`: Included, same as for the base split.
      - `r_tool_execution_errors`: Included, same as for the base split.
      - `r_policy_errors`: Included, same as for the base split.
      - `r_user_end_conversation`: User has additional instructions to end the conversation: if the ambiguity should be resolved with the user, but the assistant does not include the user but acts proactively even though ambiguity exists, then the user generates `DISAMBIGUATION_ERROR` (r=0.0); if the ambiguity can be resolved internally by the assistant, but the assistant includes the user for disambiguation, then the user also generates `DISAMBIGUATION_ERROR` (r=0.0).

- Note that the following task_ids are exluded from the results reported in the paper due to task specification errors.
  - Base: None.
  - Hallucination: 41, 54, 59, 79, 80, 84, 95.
  - Disambiguation: 1, 2, 3, 5, 35, 47.

## License

See `./LICENSE`.

## Contact

Please submit issues or pull requests if you find problems with the benchmark.
