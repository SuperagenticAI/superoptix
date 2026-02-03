"""
SuperOptiX Finance Tools
========================

Financial calculation and analysis tools for agents.
"""


class CurrencyConverterTool:
    """Currency conversion tool with mock exchange rates."""

    def __init__(self):
        # Mock exchange rates (in real implementation, would fetch from API)
        self.exchange_rates = {
            "USD": 1.0,  # Base currency
            "EUR": 0.85,
            "GBP": 0.75,
            "JPY": 110.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CHF": 0.92,
            "CNY": 6.45,
        }

    def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> str:
        """Convert currency amount between different currencies."""
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()

            if from_currency not in self.exchange_rates:
                return f"❌ Unsupported currency: {from_currency}"

            if to_currency not in self.exchange_rates:
                return f"❌ Unsupported currency: {to_currency}"

            # Convert to USD first, then to target currency
            usd_amount = amount / self.exchange_rates[from_currency]
            converted_amount = usd_amount * self.exchange_rates[to_currency]

            return f"""💱 Currency Conversion:
{"=" * 50}
{amount:,.2f} {from_currency} = {converted_amount:,.2f} {to_currency}

Exchange Rate: 1 {from_currency} = {self.exchange_rates[to_currency] / self.exchange_rates[from_currency]:.4f} {to_currency}

Note: Using mock exchange rates. In production, would use live rates from financial APIs.
"""
        except Exception as e:
            return f"❌ Currency conversion error: {str(e)}"


class TaxCalculatorTool:
    """Tax calculation utilities."""

    def calculate_income_tax(self, income: float, tax_rate: float = 0.22) -> str:
        """Calculate income tax based on income and tax rate."""
        try:
            tax_amount = income * tax_rate
            after_tax_income = income - tax_amount

            return f"""🧾 Income Tax Calculation:
{"=" * 50}
Gross Income: ${income:,.2f}
Tax Rate: {tax_rate:.1%}
Tax Amount: ${tax_amount:,.2f}
After-Tax Income: ${after_tax_income:,.2f}

Effective Tax Rate: {tax_rate:.1%}
"""
        except Exception as e:
            return f"❌ Tax calculation error: {str(e)}"

    def calculate_sales_tax(self, amount: float, tax_rate: float = 0.08) -> str:
        """Calculate sales tax for a purchase."""
        try:
            tax_amount = amount * tax_rate
            total_amount = amount + tax_amount

            return f"""🛒 Sales Tax Calculation:
{"=" * 50}
Subtotal: ${amount:.2f}
Tax Rate: {tax_rate:.1%}
Sales Tax: ${tax_amount:.2f}
Total: ${total_amount:.2f}
"""
        except Exception as e:
            return f"❌ Sales tax calculation error: {str(e)}"


class LoanCalculatorTool:
    """Loan calculation and analysis tool."""

    def calculate_loan_payment(
        self, principal: float, annual_rate: float, years: int
    ) -> str:
        """Calculate monthly loan payment using amortization formula."""
        try:
            monthly_rate = annual_rate / 12 / 100
            num_payments = years * 12

            if monthly_rate == 0:
                monthly_payment = principal / num_payments
            else:
                monthly_payment = (
                    principal
                    * (monthly_rate * (1 + monthly_rate) ** num_payments)
                    / ((1 + monthly_rate) ** num_payments - 1)
                )

            total_paid = monthly_payment * num_payments
            total_interest = total_paid - principal

            return f"""🏦 Loan Payment Calculation:
{"=" * 50}
Principal: ${principal:,.2f}
Annual Interest Rate: {annual_rate:.2f}%
Loan Term: {years} years ({num_payments} payments)

Monthly Payment: ${monthly_payment:.2f}
Total Amount Paid: ${total_paid:,.2f}
Total Interest: ${total_interest:,.2f}

Interest as % of Principal: {(total_interest / principal) * 100:.1f}%
"""
        except Exception as e:
            return f"❌ Loan calculation error: {str(e)}"


class InvestmentAnalyzerTool:
    """Investment analysis and calculation tool."""

    def calculate_compound_interest(
        self,
        principal: float,
        annual_rate: float,
        years: int,
        compounds_per_year: int = 12,
    ) -> str:
        """Calculate compound interest growth."""
        try:
            rate_per_period = annual_rate / 100 / compounds_per_year
            total_periods = compounds_per_year * years

            final_amount = principal * (1 + rate_per_period) ** total_periods
            interest_earned = final_amount - principal

            return f"""📈 Compound Interest Analysis:
{"=" * 50}
Initial Investment: ${principal:,.2f}
Annual Interest Rate: {annual_rate:.2f}%
Time Period: {years} years
Compounding: {compounds_per_year} times per year

Final Amount: ${final_amount:,.2f}
Interest Earned: ${interest_earned:,.2f}
Total Return: {((final_amount - principal) / principal) * 100:.1f}%

Growth Multiple: {final_amount / principal:.2f}x
"""
        except Exception as e:
            return f"❌ Investment calculation error: {str(e)}"


class BudgetPlannerTool:
    """Budget planning and analysis tool."""

    def analyze_budget(self, income: float, expenses_data: str) -> str:
        """Analyze budget based on income and expenses."""
        try:
            # Parse expenses data (format: "category:amount,category:amount")
            expenses = {}
            total_expenses = 0

            for expense_item in expenses_data.split(","):
                if ":" in expense_item:
                    category, amount_str = expense_item.split(":")
                    amount = float(amount_str.strip())
                    expenses[category.strip()] = amount
                    total_expenses += amount

            remaining = income - total_expenses
            savings_rate = (remaining / income) * 100 if income > 0 else 0

            # Categorize expenses
            expense_breakdown = []
            for category, amount in expenses.items():
                percentage = (amount / income) * 100 if income > 0 else 0
                expense_breakdown.append(
                    f"- {category}: ${amount:,.2f} ({percentage:.1f}%)"
                )

            status = "✅ Surplus" if remaining > 0 else "❌ Deficit"

            return f"""💰 Budget Analysis:
{"=" * 50}
Monthly Income: ${income:,.2f}
Total Expenses: ${total_expenses:,.2f}
Remaining: ${remaining:,.2f} {status}

Savings Rate: {savings_rate:.1f}%

Expense Breakdown:
{chr(10).join(expense_breakdown)}

Recommendations:
- Target savings rate: 20% or higher
- Emergency fund: 3-6 months of expenses
- Review and optimize large expense categories
"""
        except Exception as e:
            return f"❌ Budget analysis error: {str(e)}"


# Export all finance tools
__all__ = [
    "CurrencyConverterTool",
    "TaxCalculatorTool",
    "LoanCalculatorTool",
    "InvestmentAnalyzerTool",
    "BudgetPlannerTool",
]
