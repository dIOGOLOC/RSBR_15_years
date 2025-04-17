# Methodology

<span style="display:block;text-align:center">![image](/docs/source/_static/images/flowchart_method.png)


## Input data step

The methodology relies on three key input datasets, each provided in standard seismological formats to ensure compatibility with widely used seismic analysis tools:

- **Event Catalog ([GCMT-XML](https://www.globalcmt.org/))**

    The event catalog provides information about seismic events, including origin time, location, depth, and moment tensor solutions. This metadata is essential for defining event-station geometry and computing theoretical travel paths (e.g., back azimuths) via models such as TauP.

- **Waveform Data ([MSEED](https://www.fdsn.org/pdf/SEEDManual_V2.4.pdf))**

    The seismic recordings are stored in the MiniSEED format, which contains continuous or segmented time series from multiple seismic stations. These data are used to extract the signal strength, compute energy ratios, and perform waveform correlation required in the back azimuth and sensor orientation analysis.

- **Station Metadata ([StationXML](https://docs.fdsn.org/projects/stationxml/en/latest/))**

    The StationXML file includes crucial metadata such as station coordinates, sensor orientations, instrument response, and channel information. This information allows for precise waveform preprocessing, component rotation, and response corrections.


## Trimming step

In this step, waveform data are prepared for analysis through a sequence of extraction and cropping operations based on the event location and theoretical arrival times of key seismic phases. The procedure is composed of the following stages:

- **Retrieving event waveforms ([get_waveforms](https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_waveforms.html))**  
  Using the event catalog and station metadata, waveforms corresponding to each seismic event are retrieved. This ensures that all subsequent analyses are performed on data that are correctly associated with their respective earthquakes.

- **Computing epicentral distance([gps2dist_azimuth](https://docs.obspy.org/packages/autogen/obspy.geodetics.base.gps2dist_azimuth.html#obspy.geodetics.base.gps2dist_azimuth))**  
  The epicentral distance between the seismic event and the recording station is calculated using their geographic coordinates (latitude and longitude). This distance, typically expressed in degrees, is essential for estimating travel times of seismic phases.

- **Computing arrival times([taup](https://docs.obspy.org/packages/obspy.taup.html))**  
  Based on the calculated epicentral distance and utilizing standard Earth models (e.g., TauP), the expected arrival times of primary seismic phases such as **P**, **PKP**, and **PKIKP** are computed. These phases are crucial for orientation analysis, component rotation, and coherence studies.

- **Trimming waveforms([trim](https://docs.obspy.org/packages/autogen/obspy.core.stream.Stream.trim.html))**  
  For each trace, a time window is extracted around the estimated arrival time of the selected phase. A symmetrical window of ±120 seconds is applied, ensuring that the primary signal is captured while minimizing the inclusion of unrelated noise.


## Detection step

This step involves an automated analysis designed to identify reliable seismic events and assess the quality of the recorded waveforms prior to orientation analysis. The detection process begins with the systematic evaluation of each event waveform, focusing on the vertical component (HHZ) where the P-wave arrival is most prominent. The procedure comprises the following sequential operations:

- **Akaike Information Criterion (AIC)**

The AIC method (Maeda, 1985) is applied to detect the precise onset time of the P-wave. This statistical approach identifies the time at which the signal undergoes a significant change, indicating the arrival of the seismic wave.

- **Signal-to-noise ratio (SNR)**

Following arrival detection, the signal-to-noise ratio is computed (Braunmiller et al., 2020). This metric quantifies the amplitude of the signal relative to the surrounding noise, providing a measure of data quality. A reliable detection is only considered valid when SNR > 10, ensuring high-quality signals for subsequent analysis.

- **Time error estimation**

If the SNR threshold is met, the method estimates the uncertainty associated with the P-wave arrival time. This step (Zhu et al., 2020) helps to quantify the precision of the pick and is essential for error propagation in later stages.

- **Instrumental gain verification**

Lastly, the instrumental gain is assessed (Park and Ishii, 2019) to ensure consistency and comparability across different stations. Correcting for variations in sensor amplification allows for accurate computation of energy-based criteria in the orientation step.

This detection stage acts as a filter, ensuring that only events with well-defined, high-quality signals proceed to orientation analysis.

## Misorientation step

**1. Input Data**

The first step in the methodology involves preparing the input data required for the optimization process. This includes the back azimuth value (`baz`) obtained from the [TauP model](https://docs.obspy.org/packages/obspy.taup.html), which represents the theoretical direction from the seismic station to the earthquake source, expressed in degrees from North. In addition to this, four arrays are required: 

- Signal Strength (`SS`);
- Similarity between vertical and radial components (`SZR`);
- Transverse-to-Radial energy ratio (`ERTR`); and 
- Radial-to-Vertical energy ratio (`ERRZ`). 

Each of these arrays is computed for a range of azimuth angles and represents a distinct quality criterion to be considered in the cost function. These parameters are crucial as they reflect how well the seismic energy is distributed in each direction, which in turn helps infer the true back azimuth and sensor misorientation.

**2. Define the Azimuth Search Space**

To perform the optimization, it is necessary to explore a range of potential azimuth angles. This is done by defining an azimuth search space with a fixed resolution. In this implementation, the azimuth angles range from 0° to 360°, incremented in steps of `dphi = 0.1°`. The use of a fine step size ensures a high-resolution search, allowing for more precise estimation of the optimal azimuth. This array of candidate angles is generated using the numpy function `np.arange(0., 360., dphi)`. Each angle in this array will be evaluated using the cost function to determine how well it meets the desired quality criteria.

**3. Compute the Cost Function**

The core of the methodology lies in the formulation and evaluation of a cost function designed to identify the optimal azimuth. The cost function used here is defined as `cost_function = (1 - SS) + SZR + ERTR`. Each term in this expression contributes to the final score assigned to a given azimuth angle. The term `(1 - SS)` serves to minimize signal strength, which is interpreted as minimizing the energy outside the principal direction. The `SZR` term emphasizes high similarity between vertical and radial components, which typically indicates a more accurate sensor orientation. The `ERTR` term favors configurations where transverse energy is minimized relative to radial energy. Together, these components guide the algorithm toward the most plausible orientation by maximizing the cost function.

**4. Find the Angle Corresponding to the Maximum of the Cost Function**

After evaluating the cost function for each angle in the azimuth search space, the algorithm identifies the angle that yields the highest cost value. This is done using the numpy function `np.argmax(cost_function)`, which returns the index of the maximum value in the array. The corresponding angle at this index is considered the most optimal in terms of meeting the combined quality criteria. This step effectively reduces the multidimensional problem to a single best candidate, providing a direct way to estimate the true back azimuth and related parameters.

**5. Calculate the Optimal Azimuth and Sensor Misorientation**

With the index of the best azimuth determined, the corresponding angle (`phi`) is extracted and rounded to the nearest whole number for clarity. The sensor misorientation angle (`theta`) is then computed as the difference between the initial back azimuth (`baz`) and the estimated azimuth angle (`phi`). To ensure that this angle is interpreted correctly in a circular system, it is normalized to the range (-180°, 180°). This normalization accounts for the periodic nature of angular measurements and ensures consistency in interpretation. The values of `phi` and `theta` represent the core outputs of the optimization routine.

**6. Extract the Quality Criteria at the Best Index**

To further characterize the optimal azimuth identified, the corresponding values of each quality metric are retrieved from their respective arrays using the `best_index`. These include `SS_best`, `SZR_best`, `ERTR_best`, and `ERRZ_best`. These metrics provide a comprehensive summary of the signal characteristics at the optimal orientation and can be used to evaluate the robustness and reliability of the estimated parameters. By examining these values, researchers can also assess the degree of confidence in the optimization results.

**7. Output Results**

The final stage of the methodology involves compiling and returning the computed results. This includes the optimal back azimuth angle (`phi`), the sensor misorientation angle (`theta`), and the associated quality metrics (`SS_best`, `SZR_best`, `ERTR_best`, and `ERRZ_best`). These outputs can then be used for further interpretation or incorporated into larger workflows, such as seismic event characterization or sensor calibration routines. The methodology ensures that the selected azimuth configuration provides a physically meaningful and quality-optimized representation of the seismic data.
