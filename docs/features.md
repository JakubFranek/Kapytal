# Feature specification

Below are the required capabilities of Kapytal from the user's point of view.

## Accounts

The user can create accounts, which represent various places where the user keeps money (bank accounts, physical wallets etc.). These accounts can be grouped into account groups (folders), which can again be grouped into another, higher-level group. Typical usage of these groups for a household can look like this:

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

These accounts will be shown in a tree view, where the balance of these accounts will be visible. Each account supports a single currency, set by the user.

## Transactions

The user can manually enter data regarding basic financial transactions (expenses and incomes), such as the date, amount, description, category (such as Rent, Food, Leisure etc.), tags, payee, from/to account etc. This data is shown in a sortable table with filtering support.

Transactions between user's own accounts are called transfers. Transfers between accounts of different currencies are supported.

Transactions support multiple categories (the transaction amount splits between them, preserving the total).

Kapytal supports recurrent transactions, which repeat with a specified time period. The user can create these recurrent transactions and have them automatically prepared by Kapytal when the time period has elapsed for convenience.

Kapytal supports refunds of expense or income transactions, both full and partial. These special refund transactions are connected to the transactions they refund and reduce/increase the total amount paid.

### Categories

The user can create custom categories. These categories can also have sub-categories. For example: category "Food & Drink", sub-categories "Groceries", "Eating out", "Work lunch" etc.

Categories have a type_ property, which can be any of "INCOME", "EXPENSE" or "INCOME_AND_EXPENSE".

### Tags

The user can assign multiple tags to a transaction. Here are some examples of typical usage: "Christmas 2022", "Work-related", "Wedding", "Vacation Greece 6/2022" etc.

### Payees

Each income or expense transaction will have a payee (for example employer name for income, shop name for expenses). Transfers, buys or sells do not support the payee input field (it makes no sense).

## Budgets

TBD

TODO: budgets

## Envelopes

Kapytal supports envelope system, where the user can virtually allocate money across multiple accounts to various envelopes. These envelopes can represent financial goals of the user, for example an emergency fund, budget for Christmas gifts, saving for a vacation etc.

Envelopes can have set priorities: for example, if the user creates an expense, the amount will be subtracted from the envelope with the lowest priority.

TODO: envelopes

## Reports

The user can generate reports, which visually represent the transaction data either in a table or a chart. Example of a report could be a cashflow report (a time-chart showing total income and expense in each month, along with their difference) or an expense category report for a selected time-period (a pie chart showing the composition of users expenses with regards to transaction categories).

TODO: reports

## Currencies

Kapytal will support multiple currencies. The user can enable or create currencies and use them with transactions or as account currencies.

The user can also designate a single currency as a base currency. This will be the currency used for account group balances and reports.

TODO: base currency recalculation

## Financial Instruments

The user can create Buy or Sell transactions to record the buy or sale of financial instruments such as stocks or fund shares. The user can pre-define these financial instruments and update their price. The shares of these instruments will be kept in a special type of account, which can only keep financial instruments.

## Data persistence

The user can save the list of entered transactions to a JSON file. This file can be later loaded by Kapytal.

Kapytal will back itself up (create a special JSON file) every N minutes of work without saving in user-specified location different from the location of the primary JSON file.

TODO: figure out JSON saving w/ circular references (maybe UUIDs for transactions?)
