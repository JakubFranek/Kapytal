# FAQ

## What's the backstory behind Kapytal?

I started tracking my financial life in 2018 as I started investing. It seemed natural to extend the tracking from investments to day-to-day expenses as well (I think Quantified Self aka "self-knowledge through numbers" is quite cool), and I looked for a suitable tool for this purpose. I eventually settled on using MoneyWiz 3, which fulfilled most of my criteria. However, the program was retired in 2021 or so and it slowly started to break down. I was not able to find a suitable alternative and in October 2022 I eventually decided to make one myself. I have been using Kapytal to track my financial life since July 2023.

## What's the meaning of the name?

I was looking for a short yet meaningful name, one which would look and sound good but would not clash with existing projects or well known brand names. I think Kapytal fits the bill.
The word "capital" has an obvious connection to money, the "py" refers to the fact that the program is written in Python, and the "K" stands for Kuba, which is the diminutive version of my first name.

## What's up with the capybara mascots?

In Czech, capybara is spelled "kapybara". My friend mentioned the similarity with my program's name, I played around a bit with Stable Diffusion and AI-generated kapytalist kapybaras were born.

## Why even bother logging all of your transactions?

- knowledge is power
- knowing where your money goes is useful for telling whether you can afford that expensive gadget you want
- knowing what your cashflow is like is absolutely critical when making big life decisions like taking a mortgage or planning kids
- you can see how much money you have and how it is distributed across your accounts, wallets, investments and safes in one place without having to check all of those places manually
- transaction history usually disappears after a few months from your bank's internet banking interface
- logging your transactions is a must if you are splitting expenses with your partner
- like photos, your financial transactions are memories or snapshots of your life
- it doesn't take that much time (cca 15 minutes per week) and Kapytal has a few quality of life features to make it as easy for you as possible

## Why won't you support automated imports?

- there are way too many bank APIs and statement formats
- there are way too many CSV, QIF etc. formats for other financial software, which usually does not even contain all of the concepts used in Kapytal
- by "manually" logging the transactions, you are forced to mentally evaluate them, which forces you to think about whether your spending habits are reasonable
- you can't import physical cash transactions anyway
- I don't have the time or quite possibly the skills to implement it even if I wanted to

## How to handle a mortgage in Kapytal?

Mortgage is a loan, but its also an investment, as you are buying an asset that can be reasonably expected to grow in value over time. To capture this, I propose the following:

1. One-time preparation
    1. create a [Security](./glossary.md#security-icon) for your real estate
        - set the number of share decimals to zero (there will only ever be 1 share)
        - set the price of your real estate Security to whatever price you bought it for
    1. create a Security for your mortgage
        - set a high number of share decimals, as you want a fine grained resolution of shares here
        - set the price of your mortgage Security to the amount of money you borrowed
    1. create a [Security Account](./glossary.md#security-account-icon) for your real estate and mortgage [Securities](./glossary.md#security-icon)
    1. create a [Sell](./glossary.md#sell-icon) [Transaction](./glossary.md#transaction) to get your loaned amount
        - set the newly created real estate Security Account
        - set the [Cash Account](./glossary.md#transaction) you want to receive the borrowed money
        - sell exactly 1 share of your mortgage Security
        - price per share is the amount of money you borrowed
        - after this Sell Transaction, your real estate Security Account will contain exactly -1 (minus one!) share of your Mortgage, while your Cash Account will contain the money you borrowed
    1. create a [Buy](./glossary.md#buy-icon) Transaction to buy your real estate
        - set the newly created real estate Security Account again
        - set the Cash Account you want to buy the real estate from
        - buy exactly 1 share of your real estate Security
        - price per share is the price you bought the real estate for
        - after creating this Buy Transaction, your real estate Security Account will contain exactly -1 (minus one!) share of your Mortgage and +1 share of your real estate, while your Cash Account should contain zero money or so (depending on previous Transaction history)
1. Monthly logging
    1. find out what part of your monthly annuity/payment is loan interest and what part is the capital repayment
        - this changes every month!
        - you can use online annuity calculators if you do not have the precise amounts from your lender yet
    1. create the payment of the loan interest as an [Expense](./glossary.md#expense-icon)
        - the [Category](./glossary.md#category-icon) could be something like "Housing/Mortgage Interest"
    1. create the capital repayment as a [Buy](./glossary.md#buy-icon) from your bank account to a fictituous real estate Security Account
        - price per share is the amount of money you borrowed
        - total is the current month's capital repayment amount
        - the number of mortgage shares is capital repayment amount divided by the borrowed amount (should be a positive number smaller than 1)

The advantage of this approach is that when your real estate appreciates in value, your net worth grows by the same exact amount. It allows you to easily handle refinancing your mortgage, as the only thing that would change after refinancing is the monthly interest and capital repayment amounts, as well as early mortgage payoff, as you can easily model that via special [Buy](./glossary.md#buy-icon) Transaction which would pay a significant part of your mortgage off.

## How to reorder Transactions with the same date?

Edit the hours or minutes of the [Transactions](./glossary.md#transaction). You can show hours, minutes or even seconds of Transaction dates within [Transaction Table](./glossary.md#transaction) by editing the Transaction Table date format within [Settings Form](./glossary.md#settings-form) accordingly.
