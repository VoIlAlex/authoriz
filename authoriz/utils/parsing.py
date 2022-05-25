"""
Supplementary functionality for permissions parsing.
"""

from typing import List
from urllib.parse import parse_qs

from authoriz.dataclasses import ParsedAction


def merge_raw_rules_lists(rules_lists: List[List[dict]]) -> List[dict]:
    """
    Merge raw rules lists into one list.
    """
    merged_rules = []
    for rules_list in rules_lists:
        merged_rules += rules_list
    return merged_rules


def parse_action(action: str) -> ParsedAction:
    """
    Parse action plain string into dataclass.
    """
    assert isinstance(action, str)
    namespace, full_action_name = action.split(':')
    full_action_name_parts = full_action_name.split('/')
    if len(full_action_name_parts) == 1:
        action_name, params = full_action_name, None
    elif len(full_action_name_parts) == 2:
        action_name, params = full_action_name_parts
    else:
        raise RuntimeError('Action should contain only one "/".')

    if params is not None:
        params = parse_qs(params)
        for k in params:
            # TODO: support multiple values
            params[k] = params[k][0].split(',')[0]
    else:
        params = {}

    return ParsedAction(
        namespace=namespace,
        action_name=action_name,
        params=params
    )


__all__ = [
    'merge_raw_rules_lists',
    'parse_action',
]
