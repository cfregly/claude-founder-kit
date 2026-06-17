# Recorded tour

A real run of `make tour` followed by `make agent`, captured verbatim. Account resource
ids are replaced with placeholders. Reproduce it live with your own key.

```text
STEP 1  one Messages call
The Claude Messages API is Anthropic's interface that allows developers to send structured conversations to Claude and receive AI-generated responses programmatically.
stop: end_turn | tokens in 26 / out 32

STEP 2  adaptive thinking + effort
[thinking] Let ball = x, bat = x + 1.00
x + x + 1.00 = 1.10
2x = 0.10
x = 0.05
[answer] ## Reasoning

Let the ball cost **x** dollars.
Then the bat costs **x + $1.00**.

Setting up the equation:
$$x + (x + 1.00) = 1.10$$
$$2x + 1.00 = 1.10$$
$$2x = 0.10$$
$$x = 0.05$$

**Check:** Ball = $0.05, Bat = $1.05, Difference = $1.00, Total = $1.10

The ball costs **$0.05** (5 cents).
stop: end_turn | tokens in 46 / out 203

STEP 3  one tool round trip
first stop: tool_use
Claude asked for: get_exchange_rate {'code': 'EUR'}
second stop: end_turn
answer: Based on the current exchange rate, **$50 USD = 46.00 EUR**.

Here's how it's calculated:
- Exchange rate: **1 USD = 0.92 EUR**
- 50 x 0.92 = **46.00 EUR**

STEP 4  manual agent loop
turn 1 stop: tool_use
  ran find_customer({'name': 'Ada'}) -> {'id': 'c_42', 'tier': 'gold'}
turn 2 stop: tool_use
  ran get_order_count({'customer_id': 'c_42'}) -> {'orders': 7}
turn 3 stop: end_turn
answer: Ada is a Gold-tier customer who has placed 7 orders.

STEP 5  a Managed Agent end to end
env: env_XXXXXXXXXXXX | agent: agent_XXXXXXXXXXXX | session: sesn_XXXXXXXXXXXX
TOOL  : bash {'command': 'date -u +%Y-%m-%d && echo $((17*23))'}
RESULT: text='2026-06-17\n391\n'
AGENT : Today's UTC date is 2026-06-17, and 17 x 23 = 391.
[idle, stop_reason=end_turn]
session archived
```
