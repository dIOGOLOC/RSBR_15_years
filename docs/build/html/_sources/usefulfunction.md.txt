# Useful functions

## Find sensor misorientation

```{eval-rst}
.. py:function:: find_orientation(baz, SS, SZR, ERTR, ERRZ):

    Calculates optimal back-azimuth (φ) and sensor misorientation (θ) by evaluating:

    - Signal strength (SS)
    - Vertical-radial component similarity (SZR)
    - Transverse-to-radial energy ratio (ERTR)
    - Radial-to-vertical energy ratio (ERRZ)

    The cost function combines these criteria to maximize solution quality through systematic azimuth search.

    :type baz: float
    :param baz: Initial back-azimuth from taup model (degrees)
    :type SS: numpy.ndarray
    :param SS: Signal strength array (0-1 normalized)
    :type SZR: numpy.ndarray
    :param SZR: Vertical-radial similarity array (correlation coefficients)
    :type ERTR: numpy.ndarray
    :param ERTR: Transverse-to-radial energy ratios
    :type ERRZ: numpy.ndarray
    :param ERRZ: Radial-to-vertical energy ratios
    :returns: φ, θ, SS_best, SZR_best, ERTR_best, ERRZ_best
    :rtype: tuple of (float, float, float, float, float, float)
```

```{tip}
For optimal results:

- Use 0.1° azimuth search increments
- Apply quality thresholds: SZR ≥ 0.45, ERTR ≥ 0.45, ERRZ ≥ -1
- Normalize energy ratios before optimization
```

```{admonition} Formula
The optimization maximizes:

$$
\mathcal{F}(\phi) = (1-SS) + SZR + (1-ERTR)
$$

Where:
- $SS$ = Normalized transverse component energy
- $SZR$ = Vertical-radial correlation
- $ERTR$ = Transverse/Radial energy
```

-------------

## Applying the algorithm of Braunmiller & Pornsopin


```{eval-rst}
.. py:function:: Braunmiller_Pornsopin_algorithm(tr1, tr2, trZ, noise, baz, time_ins, CCVR_MIN=0.45, SNR_MIN=10, TRR_MIN=0.45, RVR_MIN=-1):

    Implements the P-wave particle motion analysis for:

    - Back-azimuth estimation
    - Sensor misorientation detection
    - Instrument gain calculation
    - Data quality assessment

    Applies five quality criteria with configurable thresholds.

    :type tr1: numpy.ndarray
    :param tr1: First horizontal component (typically North)
    :type tr2: numpy.ndarray
    :param tr2: Second horizontal component (typically East)
    :type trZ: numpy.ndarray
    :param trZ: Vertical component
    :type noise: numpy.ndarray
    :param noise: Noise window for SNR calculation
    :type baz: float
    :param baz: Theoretical back-azimuth (degrees)
    :type time_ins: float
    :param time_ins: Observed-predicted time difference (seconds)
    :returns: Dictionary containing 15 result metrics
    :rtype: dict
```

```{important}
**Quality Criteria Thresholds**:

1. SNR ≥ 10 dB
2. Vertical-radial correlation ≥ 0.45
3. Transverse/radial ratio ≤ 0.55 (ERTR ≥ 0.45)
4. Time residual |Δt| < 90s
5. Radial/vertical ratio > user-defined (default: -1)
```

```{admonition} Component rotation implemented as:

$$
\begin{pmatrix}
R \\ 
T 
\end{pmatrix} = 
\begin{pmatrix}
\cos\phi & \sin\phi \\ 
-\sin\phi & \cos\phi  
\end{pmatrix}
\begin{pmatrix}
H_1 \\ 
H_2 
\end{pmatrix}
$$

Where energy ratios are calculated as:

$$
ERTR = 1 - \frac{\int T^2(t)dt}{\int R^2(t)dt}
$$

$$
ERRZ = 1 - \frac{\int R^2(t)dt}{\int Z^2(t)dt}
$$
```


```{seealso}
- Braunmiller, J.,J. Nabelek, and A. Ghods (2020). Sensor Orientation of Iranian Broadband Seismic Stations from P-Wave Particle Motion, Seismol. Res. Lett. 91, 1660–1671, doi: 10.1785/0220200019.

- Pornsopin, P., Pananont, P., Furlong, K.P. et al. Sensor orientation of the TMD seismic network (Thailand) from P-wave particle motions. Geosci. Lett. 10, 24 (2023). https://doi.org/10.1186/s40562-023-00278-7.

- Zhu, G., H. Yang,J. Lin, and Q. You (2020). Determining the Orientation of Ocean-Bottom Seismometers on the Seafloor and Correcting for Polarity Flipping via Polarization Analysis and Waveform Modeling, Seismol. Res. Lett. XX, 1–12, doi: 10.1785/0220190239.
```