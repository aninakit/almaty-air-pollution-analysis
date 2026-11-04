# Domain Model — Almaty Air Pollution Analysis

## 1. Research Objective

This research investigates the relationship between
the heating season, calm wind conditions, and PM2.5
air pollution in Almaty, Kazakhstan.

The study focuses on two hypotheses:

- H1: PM2.5 concentration is higher during the
  heating season than during the non-heating season.
- H2: The combination of the heating season and
  calm wind conditions increases the probability
  of a PM2.5 pollution spike.

## 2. Mathematical Formalization

### Hypothesis H1 — Seasonal Difference

The primary seasonal difference is defined as:

$$
\Delta \mu =
\mu_{\text{heating}} -
\mu_{\text{non-heating}}
$$

Where:

- $\mu_{\text{heating}}$: Mean PM2.5 concentration
  during the heating season.
- $\mu_{\text{non-heating}}$: Mean PM2.5 concentration
  outside the heating season.

The alternative hypothesis is:

$$
H_1: \Delta \mu > 0
$$

### Hypothesis H2 — Logistic Regression

Pollution spikes are represented by a binary variable:

$$
Y_i =
\begin{cases}
1, & PM_{2.5,i} > 35 \\
0, & PM_{2.5,i} \leq 35
\end{cases}
$$

The proposed logistic regression model is:

$$
\log\left(\frac{p_i}{1-p_i}\right)
=
\beta_0 +
\beta_1 H_i +
\beta_2 C_i +
\beta_3(H_i C_i)
$$

Where:

- $p_i$: Probability of a pollution spike.
- $H_i$: Heating season indicator (0 or 1).
- $C_i$: Calm wind indicator (0 or 1).
- $\beta_3$: Interaction coefficient.

A positive interaction coefficient indicates
a positive interaction on the log-odds scale.


### Loss Function — Binary Cross-Entropy

The proposed logistic regression model uses
Binary Cross-Entropy (Log Loss):

$$
L = -\frac{1}{N}
\sum_{i=1}^{N}
\left[
y_i \log(p_i) +
(1-y_i)\log(1-p_i)
\right]
$$

Where:

- $L$: Binary Cross-Entropy loss.
- $N$: Number of observations.
- $y_i$: Actual binary outcome (0 or 1).
- $p_i$: Predicted probability of a PM2.5 spike.

The objective is to minimize the loss function.

A lower loss indicates better predicted probabilities
on the evaluated dataset.

### Target Evaluation Metrics

The proposed model will be evaluated using:

- Log Loss — quality of predicted probabilities.
- ROC-AUC — ability to distinguish spike and non-spike cases.
- Precision — proportion of predicted spikes that are correct.
- Recall — proportion of actual spikes detected.

These metrics will only be calculated after collecting
a sufficiently large dataset and fitting the model.


## 3. Mathematical Notation

| Symbol | Description | Unit |
|---|---|---|
| PM2.5 | Fine particulate matter concentration | µg/m³ |
| H | Heating season indicator | Binary |
| C | Calm wind indicator | Binary |
| Y | Pollution spike indicator | Binary |
| p | Probability of pollution spike | Probability |
| β0 | Logistic regression intercept | Unitless |
| β1 | Heating season coefficient | Unitless |
| β2 | Calm wind coefficient | Unitless |
| β3 | Interaction coefficient | Unitless |
| Δµ | Seasonal mean difference | µg/m³ |

## 4. Benchmark Performance Metrics

The data processing pipeline is evaluated using:

- Mean execution latency (ms)
- Median execution latency (ms)
- P95 and P99 latency (ms)
- Standard deviation (ms)
- Bootstrap 95% confidence interval for mean latency
- Error rate (%)

The first five benchmark runs are excluded
as warm-up measurements.

## 5. Reproducibility

- Random seed: 42
- Warm-up runs: 5
- Evaluation runs: 30
- Benchmark results: `data/raw/test_run.jsonl`
- Processed metrics: `data/processed/metrics_summary.csv`

## 6. Limitations

The current environmental dataset contains only
8 sample observations.

Therefore, the current analysis does not establish
statistically reliable conclusions about seasonal
air pollution or pollution spike probability.

The logistic regression model is a proposed method,
not a fitted or validated model.

Benchmark results describe execution performance
on the tested computer and dataset.


## 7. Formal target metrics and evaluation protocol

Let $D=\{(x_i,y_i)\}_{i=1}^{N}$, with
$x_i=(1,H_i,C_i,H_iC_i)^T$ and $C_i=\mathbf{1}[w_i<1.0\;\mathrm{m/s}]$.
The probability model is $p_i=\sigma(\beta^T x_i)$, where
$\sigma(z)=1/(1+e^{-z})$. The 35 microgram per cubic meter spike
threshold is an operational project setting, not a regulatory limit.

For a fixed decision threshold $\tau=0.5$, define
$\hat y_i=\mathbf{1}[p_i\geq\tau]$. Then

$$
TP=\sum_i\mathbf{1}[y_i=1,\hat y_i=1],\quad
FP=\sum_i\mathbf{1}[y_i=0,\hat y_i=1],\quad
FN=\sum_i\mathbf{1}[y_i=1,\hat y_i=0].
$$

$$
\mathrm{Precision}=\frac{TP}{TP+FP},\qquad
\mathrm{Recall}=\frac{TP}{TP+FN}.
$$

Report a metric as undefined if its denominator is zero. With positive
indices $P=\{i:y_i=1\}$ and negative indices $Q=\{j:y_j=0\}$,

$$
\mathrm{AUC}=\frac{1}{|P||Q|}\sum_{i\in P}\sum_{j\in Q}
\left(\mathbf{1}[p_i>p_j]+\tfrac12\mathbf{1}[p_i=p_j]\right).
$$

AUC requires both classes. Log loss, defined above, is the primary probability
metric; clip numerical probabilities to $[\epsilon,1-\epsilon]$ before taking
logs, with $\epsilon=10^{-15}$. AUC, precision, and recall are secondary metrics.

| Symbol | Meaning | Unit or range |
|---|---|---|
| $i,j,N$ | Observation indices and sample size | Counts |
| $x_i,D$ | Feature vector and dataset | Mixed / dataset |
| $w_i$ | Wind speed | m/s |
| $\sigma,\beta$ | Logistic function and coefficient vector | Probability / log odds |
| $y_i,\hat y_i,\tau$ | True label, predicted label, decision threshold | 0 or 1 / probability |
| $TP,FP,FN$ | True positives, false positives, false negatives | Counts |
| $P,Q$ | Positive and negative observation index sets | Sets |
| $\epsilon$ | Numerical clipping constant | Probability |
| $\mathbf{1}[A]$ | Indicator of event A | 0 or 1 |
| $t_k,m,s,B$ | Successful run latency, count, sample SD, bootstrap replicates | ms / count / ms / count |

For benchmark latency, exclude warm-up runs, count failures over all evaluation
attempts, and calculate latency statistics from successful attempts only:

$$
\bar t=\frac1m\sum_{k=1}^m t_k,\quad
s=\sqrt{\frac{\sum_{k=1}^m(t_k-\bar t)^2}{m-1}},\quad
\mathrm{ErrorRate}=100\frac{n_{\mathrm{failed}}}{n_{\mathrm{evaluation}}}\%.
$$

Here $n_{\mathrm{failed}}$ and $n_{\mathrm{evaluation}}$ are counts of failed
and total evaluation attempts. Use $B=10{,}000$ resamples with replacement,
each of size $m$, seed 42, and the 2.5th and 97.5th percentiles of resampled
means for the percentile bootstrap CI. Report p95 and p99 with NumPy's linear
percentile interpolation. With only 30 trials these tail estimates are unstable.
The CI concerns the mean latency, not 95% of individual runtimes.

For future model training, split real observations chronologically before
fitting preprocessing; keep the final test period untouched and account for
sensor and time dependence. Do not treat repeated rows as independent training
samples. In the current 8-row sample all heating observations are spikes and
all non-heating observations are non-spikes: complete separation prevents
reliable unregularized logistic coefficient inference. The calm/non-heating
combination is absent. No fitted interaction effect or p-value is reported.
An observational seasonal contrast alone does not identify a causal effect.

## External observation unit

The independent data source for the seasonal description is AirData.kz. Each record is a city-day cluster average. The observed contrast uses the same difference-of-means equation as H1, substituting calendar winter and summer for heating status. The project threshold for a spike was defined for individual sample readings. The daily aggregate has a different time scale and carries no wind field, so the H2 interaction remains a proposed model. [Sampling frame and attribution](../data/environment/README.md).
