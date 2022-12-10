from src.models.accounts.account_group import AccountGroup
from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin

# TODO: make un-instantiatable? Test only sub-classes, incl. mixins...


class Account(NameMixin, DatetimeCreatedMixin):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self._parent: AccountGroup | None = None

    @property
    def parent(self) -> AccountGroup | None:
        return self._parent

    @parent.setter
    def parent(self, new_parent: AccountGroup | None) -> None:
        if new_parent is not None and not isinstance(new_parent, AccountGroup):
            raise TypeError("Account.parent must be an AccountGroup or a None.")

        if self._parent is not None:
            self._parent._children.remove(self)

        if new_parent is not None:
            new_parent._children.append(self)

        self._parent = new_parent
