# DATA-APP-D2 A-Share Minimum Schema

Status: completed

Purpose:
- Define A-share daily minimum schema for DATA-APP.
- Separate required fields from optional enrichment fields.
- Keep schema validation read-only and paper-only.

Required market fields:
- date
- symbol
- name
- open
- high
- low
- close
- prev_close
- volume
- amount

Required status fields:
- turnover_rate
- float_market_cap
- total_market_cap
- listing_days
- is_st

Required risk and sector fields:
- limit_up_price
- limit_down_price
- sector_code
- sector_name
- trading_status

Optional enrichment fields:
- dragon_tiger_list
- announcement_summary
- research_summary
- northbound_flow
- etf_flow
- fund_flow_proxy
- news_catalyst
- limit_up_history

Safety:
- paper-only
- local-only
- read-only
- no real exchange API
- no real brokerage API
- no API key
- no real order
- no real execution
- no real money impact
- operator review required
