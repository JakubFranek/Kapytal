# Feature specification

Below are the required capabilities of Kapytal from the user's point of view.

## Accounts

The user can create Accounts, which represent various places where the user keeps money (bank accounts, physical wallets etc.). These accounts can be grouped into Account Groups (folders), which can again be grouped into another, higher-level group. Typical usage of these groups for a household can look like this:

> - Adam
>   - Cash
>     - Wallet
>     - Cash at home
>   - Current Accounts
>     - Bank A
>     - Bank B
>   - Savings Accounts
>     - ...
>   - Pension Funds
>     - ..
> - Eve
>   - ...
> - Shared Finances
>   - ...

These Accounts are be shown in a tree view, where the balance of these Accounts is be visible. There are two types of Accounts: Cash Accounts and Security Accounts. You can read more about Accounts [here](/docs/accounts.md).

## Currencies and Exchange Rates

Kapytal supports multiple Currencies. The user can enable or create Currencies and use them with Transactions or as Cash Account Currencies.

The user can also designate a single Currency as a "base" Currency. This will be the Currency used for calculating balances and reports.

## Transactions

The user can manually enter data regarding basic financial transactions (expenses and incomes), such as the date, amount, description, Category (such as Rent, Food, Leisure etc.), Tags, Payee, from/to Accounts etc. This data is shown in a sortable table with filtering support.

Transactions between user's own accounts are called Transfers. Transfers between Accounts of different currencies are supported, and are used to represent Currency exchanges.

Transactions support multiple categories (the transaction amount splits between them, preserving the total).

Kapytal supports recurrent transactions, which repeat with a specified time period. The user can create these recurrent transactions and have them automatically prepared by Kapytal when the time period has elapsed for convenience.

Kapytal supports refunds of expense or income transactions, both full and partial. These special refund transactions are connected to the transactions they refund and reduce/increase the total amount paid.

You can read more about Transactions [here](/docs/transactions.md).

### Categories

The user can create custom categories. These categories can also have sub-categories. For example: Category "Food & Drink", sub-categories "Groceries", "Eating out", "Work lunch" etc.

There are three Category types: "Income", "Expense" and "Income and Expense".

### Tags

The user can assign multiple tags to a transaction. Here are some examples of typical usage: "Christmas 2022", "Work-related", "Wedding", "Vacation Greece 6/2022" etc.

### Payees

Each income or expense Transaction will have a Payee (for example employer name for income, shop name for expenses). Transfers, buys or sells do not support the payee input field (it makes no sense).

## Securities

The user can create Buy or Sell transactions to record the buy or sale of financial instruments such as stocks or fund shares. The user can pre-define these financial instruments and update their price. The shares of these instruments will be kept in a special type of account, which can only keep financial instruments.

## Reports

The user can generate reports, which visually represent the transaction data either in a table or a chart. Example of a report could be a Cash Flow report (a time-chart showing total income and expense in each month, along with their difference) or an expense category report for a selected time-period (a pie chart showing the composition of users expenses with regards to transaction categories).

## Data persistence

The user can save the list of entered transactions to a JSON file. This file can be later loaded by Kapytal.
