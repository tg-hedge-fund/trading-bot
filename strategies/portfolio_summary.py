import time

from api_utils.groww_api_handlers import get_portfolio, stream_live_data_by_quote
from utils.constants import MESSAGE_TYPES
from utils.discord_bot import send_message_via_discord_bot

# format of the message:
# Company name:
#   current value
#   invested value
#   % of stake in pf

def get_portfolio_details():
    pf_summary = get_portfolio()
    companies = {}
    if pf_summary is not None:
      total_pf_value = 0
      for company in pf_summary["holdings"]:
          current_company = company["trading_symbol"]
          live_quote = stream_live_data_by_quote("NSE", "CASH", current_company)
          if live_quote is not None:
              current_stake = live_quote["last_price"] * company["quantity"]
              invested_value = company["quantity"] * company["average_price"]
              total_pf_value += current_stake

              companies[current_company] = {
                  "Current Value": current_stake,
                  "Invested Value": invested_value,
                  "Absolute Returns": ((current_stake - invested_value) / invested_value) * 100,
              }

          time.sleep(1)

      # total_pf_value is now fully summed, so compute each holding's stake in the portfolio
      for details in companies.values():
          details["Percentage Stake"] = (details["Current Value"] / total_pf_value) * 100

      message = format_portfolio_message(companies, total_pf_value)
      send_message_via_discord_bot(message, MESSAGE_TYPES.PORTFOLIO)


def format_portfolio_message(companies, total_pf_value):
    lines = ["**Portfolio Summary**", ""]
    for name, details in companies.items():
        lines.append(f"**{name}**")
        lines.append(f"  Current Value: ₹{details['Current Value']:,.2f}")
        lines.append(f"  Invested Value: ₹{details['Invested Value']:,.2f}")
        lines.append(f"  Absolute Returns: {details['Absolute Returns']:.2f}%")
        lines.append(f"  Percentage Stake: {details['Percentage Stake']:.2f}%")
        lines.append("")
    lines.append(f"**Total Portfolio Value: ₹{total_pf_value:,.2f}**")
    return "\n".join(lines)

