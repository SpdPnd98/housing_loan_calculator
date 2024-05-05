import csv
import json
import yaml
import math

def show_month_payment(starting_year, ending_principle, paid_mothly_principle, paid_monthly_interest):
    ending_principle += sum(paid_mothly_principle)
    for month_number, (paid_principle, paid_interest) in enumerate(zip(paid_mothly_principle, paid_monthly_interest)):
        total_paid = paid_principle + paid_interest
        ending_principle -= paid_principle
        print(f"  Month {(month_number + 1) % 12} of {starting_year + math.floor((month_number + 1) / 12)}")
        print(f"    Interest paid: {paid_interest:.2f}")
        print(f"    Principle paid: {paid_principle:.2f}")
        print(f"  Total paid: {total_paid:.2f}, interest-principle {paid_interest/total_paid:.2f} : {paid_principle / total_paid:.2f}")
        print(f"  Principle left: {ending_principle:.2f}")

with open('config/housing.yaml') as f:
    data = yaml.safe_load(f)
    print(data)

    house_price = data["house"]["price"]
    loanable_amount = house_price * data["house"]["percentage_loan"]

    current_interest_rate = data["house"]["current_interest"]
    current_interest = loanable_amount * current_interest_rate / 12 # per month payment
    adjust_interest_per_anum = data["house"]["expected_annual_increment"] # per anum adjustment
    period = data["house"]["loan_period"] * 12 # number of times of payments to be made
    total_period = period

    starting_year = data["house"]["starting_year"]

    print(f"House price: {house_price}")
    print(f"  downpayment amount: {house_price - loanable_amount}")
    print(f"  loanable amount: {loanable_amount}")
    print(f"  current_interest: {current_interest}")

    print("Calculating monthly commitment without expected interest rise")

    monthly_interest = []
    monthly_principal = []
    monthly_payment = []
    ending_interest = current_interest
    ending_principal = loanable_amount
    # Payment = P x (r / n) x (1 + r / n)^n(t)] / (1 + r / n)^n(t) - 1
    total_paid = loanable_amount * (current_interest_rate / 12) \
        * ((1 + current_interest_rate / 12)**total_period) / ((1 + current_interest_rate / 12)**(total_period) - 1)
    print(f"Monthly payment is {total_paid}")
    full_amount_paid = 0
    
    yearly_interest = []
    yearly_principle = []
    yearly_payment = []

    while period >= 0:
        if len(monthly_interest) % 12 == 0 and len(monthly_interest) > 0:
            print("========================================================================")
            print(f"{starting_year + math.floor(len(monthly_interest) / 12) - 1}")
            this_year_principle = sum(monthly_principal[-12:])
            this_year_interest = sum(monthly_interest[-12:])
            this_year_payment = sum(monthly_payment[-12:])
            yearly_principle += [this_year_principle]
            yearly_interest += [this_year_interest]
            yearly_payment += [this_year_payment]
            print(f"Principle paid: {(this_year_principle):.2f}")
            print(f"Interest paid: {(this_year_interest):.2f}")
            print(f"Adjusted monthly payment is {total_paid} at interest rate of {current_interest_rate}")
            show_month_payment(starting_year, ending_principal, monthly_principal[-12:], monthly_interest[-12:])

            if period == 0:
                from prettytable import PrettyTable
                import calendar

                with open(f'{adjust_interest_per_anum}_{data["house"]["loan_period"]}y_{loanable_amount}_{data["export_data"]["destination"]["monthly"]}', 'w+') as f:
                    table = PrettyTable()
                    table.field_names= ["Month, Year", "Payment", "Paid Principle", "Paid Interest", "Loan Remaining"]
                    current_principle_remaining = loanable_amount
                    total_paid = 0
                    for month, (pay, (p, i)) in enumerate(zip(monthly_payment, zip(monthly_principal, monthly_interest))):
                        current_principle_remaining -= p
                        table.add_row([f"{calendar.month_name[month%12 + 1]} {starting_year + math.floor(month / 12)}", "{:.2f}".format(pay), "{:.2f}".format(p), "{:.2f}".format(i), "{:.2f}".format(current_principle_remaining)])
                        total_paid += pay
                    table.align["Month, Year"] = "r"
                    f.write(table.get_string())
                    f.write(f"\nTotal paid: {total_paid}")

                with open(f'{adjust_interest_per_anum}_{data["house"]["loan_period"]}y_{loanable_amount}_{data["export_data"]["destination"]["yearly"]}', 'w+') as f:
                    table = PrettyTable()
                    table.field_names= ["Year", "Payment", "Paid Principle", "Paid Interest", "Loan Remaining"]
                    current_principle_remaining = loanable_amount
                    total_paid = 0
                    for year, (pay, (p, i)) in enumerate(zip(yearly_payment, zip(yearly_principle, yearly_interest))):
                        current_principle_remaining -= p
                        table.add_row([f"{starting_year + year}", "{:.2f}".format(pay), "{:.2f}".format(p), "{:.2f}".format(i), "{:.2f}".format(current_principle_remaining)])
                        total_paid += pay
                    table.align["Month, Year"] = "r"
                    f.write(table.get_string())
                    f.write(f"\nTotal paid: {total_paid}")
                break
                


            # revise payment every year
            # Payment = P x (r / n) x [(1 + r / n)^n(t)] / [(1 + r / n)^n(t) - 1]
            current_interest_rate = current_interest_rate + adjust_interest_per_anum
            total_paid = ending_principal * (current_interest_rate / 12) \
                * ((1 + current_interest_rate / 12)**period) / ((1 + current_interest_rate / 12)**(period) - 1)

        this_interest = ending_principal * current_interest_rate / 12
        this_principal = total_paid - this_interest
        full_amount_paid += this_interest + this_principal

        monthly_interest += [this_interest]
        monthly_principal += [this_principal]
        monthly_payment += [total_paid]

        period -= 1

        ending_principal = ending_principal - this_principal
        ending_interest = this_interest

    print(f"\nLeft Loan Amount: {ending_principal:.2f}")
    print(f"Total paid is: {full_amount_paid}")



