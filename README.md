# Authoriz


The python module to allow rules-based authorization. Rules for allowing and disallowing actions can
come from different sources.

## Features

- Easy rules parsers customization. Rules could be parsed from any source.
- Specify required actions to your DRF ViewSet actions.
- Action namespace definition with action params listing.
- Fast authorization after setup is done.
- Easy parameters getters definition.
- Flexible configuration.

## Installation

To install project with pip use:
```
pip install authoriz
```

To install it to your Django project add it to your installed apps:

```python
INSTALLED_APPS = [
    ...
    'authoriz',
    ...
]
```

## Usage

The main workflow of the usage are the following:
1. **Specify action namespace enum classes.** You should predefine namespaces with actions to parse and use it.
2. **Specify parsers for the rules.** There are default parsers, 
   but it's possible (and recommended in many cases) to define
   your own with required source.
3. **Specify permissions to retrieve parameters.** Views could have specific parameters for the action.
   So you should specify getters of those in permission class.
4. **Install authorization to your view.** After all the above steps are complete,
   you can finally install authorization to specific view. It includes defining of 
   actions required by the view, adding mixin to the view and adding permission classes
   to fetch required parameters.

### 1. Specify action namespace enum classes

The enum class the following structure as the example below:

```python
from django.db import models
from authoriz.namespaces.base import ActionsNamespace


class EntityPermissions(ActionsNamespace):
    name = 'entity'

    class Actions(models.TextChoices):
        ENTITY_CREATE = 'entity:EntityCreate', 'Create entity'
        ENTITY_LIST = 'entity:EntityList', 'List entities'
        ENTITY_RETRIEVE = 'entity:EntityRetrieve', 'Retrieve entity'
        ENTITY_UPDATE = 'entity:EntityUpdate', 'Update entity'
        ENTITY_DESTROY = 'entity:EntityDestroy', 'Delete entity'

    params = {
        Actions.ENTITY_CREATE.value: [],
        Actions.ENTITY_LIST.value: [],
        Actions.ENTITY_RETRIEVE.value: ['entity_id'],
        Actions.ENTITY_UPDATE.value: ['entity_id'],
        Actions.ENTITY_DESTROY.value: ['entity_id'],
    }
```

**Parameters:**
* `name` - name of the namespace.
* `Actions` - enum class with actions contained by the given namespace.
* `params` - specification of the params allowed by specific actions. 
                If the action is not presented in dict, the empty list
                is used as a default.


### 2. Specify parsers for the rules

The parser class has the following structure as the example below:

```python
from path.to import get_rules_from_some_source
from authoriz.parsing.base import PermissionsRule, PermissionsParser

class RulesFromSomeSourceParser(PermissionsParser):
    def get_rules(self) -> List[PermissionsRule]:
        rules = get_rules_from_some_source()
        return rules
```

So the main method is `get_rules()`. It is used to specify the routine to get / parse rules list from 
any source (database, file, API call, etc.).

After you defined your required parser classes you should specify them in `settings.py` of your Django project.

```python
AUTHORIZ_RULES_PARSERS = [
    {
        'parser': 'path.to.RulesFromSomeSourceParser',
        'args': [],
        'kwargs': {},
    }
]
```

The parsers should be listed in the correct order. The rules parsed with last parsers could 
override the rules of the first ones.

#### Rule structure

```python
@dataclass
class PermissionsRule:
    name: str
    effect: str
    actions: List[ParsedAction]
    target: str
    id: int  # generated
```

**Parameters:**
* `name` - name of the rule.
  * _'Some rule #1'_
* `effect` - what exactly does the rule mean.
  * _'allow'_
  * _'deny'_
* `actions` - list of actions on which the rule has effect.
* `target` - who is the rule apply on.
  * _'132342'_ - user ID
  * _'role:admin'_ - user role
* `id` - ID of the rule. Used to sort rules before composing final allow/deny tree. *Generated automatically*.
  * _1_
  * _2_
  * _3_

#### Action structure

```python
@dataclass
class ParsedAction:
    namespace: str
    action_name: str
    params: dict  # {} by default
```

**Parameters:**
* `namespace` - namespace of the action.
  * _'project'_
  * _'entity'_
  * _'user'_
* `action_name` - exact name of the action in the given namespace.
  * _'CreateProject'_
  * _'UpdateUser'_
  * _'DeleteEntity'_
* `params` - some additional data for the given action. Allowed params are specified by namespace enum class.
  * _{project_id: 12, entity_id: 32}_


## 3. Specify permissions to retrieve parameters

The permission class has the following structure:

```python
from authoriz.permissions.base import BaseServicePermission

class EntityKwargsHasPermission(BaseServicePermission):
    def get_entity_id(self, request, view):
        return request.parser_context['kwargs']['entity_id']
```

Getters are all the methods that starts with `get_` prefix. 
Everything that goes after `get_` is considered as parameter name.
So if we make a request to the route `/entities/<entity_id>` such as:
```
GET http://<host>:<port>/entities/1232
```

it will pass param `entity_id` with value `1232` to the permission check and find
out whether your rules set allows the action with the following params or not.


## 4. Install authorization to your view

After all the previous steps are done we can apply in of the view:

```python
from rest_framework import permissions, viewsets, mixins
from authoriz.mixins import APIViewPermissionsMixin
from path.to import EntityKwargsHasPermission
from path.to import EntityPermissions

class EntityViewSet(APIViewPermissionsMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        EntityKwargsHasPermission,
    ]
    actions_permissions = {
        'create': [
            EntityPermissions.Actions.ENTITY_CREATE
        ],
        'list': [
            EntityPermissions.Actions.ENTITY_LIST
        ],
        'retrieve': [
            EntityPermissions.Actions.ENTITY_RETRIEVE,
        ],
        'update': [
            EntityPermissions.Actions.ENTITY_UPDATE,
        ],
        'destroy': [
            EntityPermissions.Actions.ENTITY_DESTROY,
        ],
    }
```

To apply follow the following steps:
1. Add `APIViewPermissionsMixin` as your first base class.
2. Add `EntityKwargsHasPermission` to `permission_classes`.
3. Specify required actions to DRF ViewSet actions in `actions_permissions`.

## License

The project is licensed under the BSD license.