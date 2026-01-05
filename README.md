# SEC Company Facts

A minimal Python library for fetching yearly 10-K company facts from [data.sec.gov](https://data.sec.gov/)
in dictionary or Pandas DataFrame format.

Only supports 10-K reports.

Example:

```py
from sec_company_facts import CompanyFacts
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt

company = CompanyFacts.from_ticker("AAPL")

df = company.get_yearly_dataframe(
    [
        "NetIncomeLoss",
        ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],
        "PaymentsForRepurchaseOfCommonStock",
    ]
)

df["Net Income ($B)"] = df["NetIncomeLoss"] / 1_000_000_000
df["Dividends + Buybacks ($B)"] = (
    df["PaymentsOfDividendsCommonStock"] + df["PaymentsForRepurchaseOfCommonStock"]
) / 1_000_000_000

print(df)

plt.plot(df.index, df["Net Income ($B)"], marker="o", label="Net Income")
plt.plot(
    df.index, df["Dividends + Buybacks ($B)"], marker="o", label="Dividends + Buybacks"
)
ax = plt.gca()
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.ylim(bottom=0)
plt.title("Dividends + buybacks, and income")
plt.xlabel("Fiscal Year")
plt.ylabel("$ billions")
plt.grid(True, alpha=0.7)
plt.legend()
plt.savefig("payout_ratio.svg")
plt.show()
```
