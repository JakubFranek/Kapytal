# Accounts

Accounts are key objects in Kapytal. Each transaction is related to one or two Accounts (although Accounts themselves are not aware of Transactions!). The user can create Accounts, which represent various places where the user keeps money (bank accounts, physical wallets etc.). These Accounts can be grouped into Account groups (folders), which can again be grouped into another, higher-level group and so on.

There are two types of Accounts: the **CashAccount** and the **SecurityAccount**. The **CashAccount** is used for money of all sorts, while the **SecurityAccount** is used for holding securities only and can contain no cash. Both types are implementations of the **Account** Abstract Base Class (ABC).

## Account properties

- Name (string)
- Date Created (datetime)
- Date Last Edited (datetime)

## Cash Account properties

- Initial balance (Decimal)
- Balance (Decimal)
- Currency (Currency)

## Security Account properties

- Securities (dictionary: {Security: int} representing Securities and the number of shares)
