# workflow_financial_ts


A workflow to store financial timeseries data into mongodb and development of trading signals.

1. While conceptually simple, the development of a robust pipeline to pull and store data is not straightforward. Considerations include ensuring no data errors or dropouts.
2. The development of trading signals is also more invovled that it first appears. Visual cues which are easily recognizable to the human eye are not easily translated to code. Even when translation to code could be achieved, the speed at which the code is running might not be fast enough for practical use when evaluating trade signals for multiple contracts in low latency. Hence, this workflow will also have to include integration of C and/or C++ codes with Python and R to boost the performance of some of these functions.

