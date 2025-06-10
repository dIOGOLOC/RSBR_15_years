# Importing modules

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter,ScalarFormatter,FuncFormatter
from matplotlib.dates import YearLocator, MonthLocator, DayLocator, HourLocator, MinuteLocator, SecondLocator, DateFormatter
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.dates as mdates

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from obspy.signal.rotate import rotate_ne_rt
from obspy.taup import TauPyModel
from obspy.imaging.beachball import beach

import os
import numpy as np


# Sets the global font size
plt.rcParams.update({'font.size': 14}) 

# --------- #
# Functions #
# --------- #

def format_y_ticks(value, _):
    '''
    Format y-label to degrees
    '''
    return f"{value:.0f}°"


def plotting_event_orientation(df_row,ORIENTATION_OUTPUT=ORIENTATION_OUTPUT):
    df_row = df_row[1]

    # -------------------------------------------
    # Function estimates the Akaike Information directly from data 
    # For a given time series
    # The Summed Log Likelihood section implies that a natural 
    # changepoint estimate is the sample index that minimizes 
    # the AIC in equation
    
    aic_curve = df_row['aic_curve']

    k_min_index = np.argmin(aic_curve)
                            
    amp_P_arr = aic_curve[k_min_index]
    time_P_arr = df_row['clock_error']
    
    # Time instability:
    time_ins = df_row['clock_error']

    if time_ins > 0:
        signal_window_start = time_ins
        signal_window_final = time_ins+TIME_FINAL_P
        noise_window_start = time_ins
        noise_window_final = time_ins-TIME_FINAL_P
    else:
        signal_window_start = time_ins
        signal_window_final = TIME_FINAL_P+time_ins
        noise_window_start = time_ins
        noise_window_final = -(abs(time_ins)+TIME_FINAL_P) 
    # -------------------------------------------------------------------------------------------------------------------------------
    # Signal and noise windows
            
    signal_window = (df_row['trZ_time'] >= signal_window_start) & (df_row['trZ_time'] <= signal_window_final)
    noise_window = (df_row['trZ_time'] >= noise_window_final) & (df_row['trZ_time'] <= noise_window_start)
                                    
    noise = df_row['trZ_data'][noise_window]
    trZ_noise_time = df_row['trZ_time'][noise_window]
            
    tr2 = df_row['tr2_data'][signal_window]
    tr1 = df_row['tr1_data'][signal_window]
    trZ = df_row['trZ_data'][signal_window]
    trZ_signal_time = df_row['trZ_time'][signal_window]
                
    # --------------------
    # figure 
    fig = plt.figure(figsize=(15, 7),constrained_layout=True)

    qc_symbol = '[✔]' if df_row['quality'] == 'good' else '[✘]'

    fig.suptitle(
    f"{qc_symbol} Evento: {df_row['evname']} "
    f"(Δ: {round(df_row['gcarc'])}° | M: {round(df_row['evmag'],1)} {df_row['evtype']} | "
    f"D: {round(df_row['evdp'])} km | C: {df_row['event_class']}) \n "
    f"SNR: {df_row['SNR']} dB | BAZ: {round(df_row['baz'])}° | "
    f"PHI: {df_row['phi']}° | theta: {df_row['theta']}° | "
    f"TI: {df_row['clock_error']}s | "
    f"GN: {df_row['gain_HHN']:.2e} | GE: {df_row['gain_HHE']:.2e}  | GZ: {df_row['gain_HHZ']:.2e}", 
    fontsize=15)    
    
    # creating grid
    gs = fig.add_gridspec(1, 2,width_ratios=[5,1])

    gs0 = gs[0].subgridspec(4, 1,height_ratios=[5,5,5,1])
    gs1 = gs[1].subgridspec(4, 1)
                                
    # Rotating components
    new_R, new_T = rotate_ne_rt(df_row['tr1_data'], df_row['tr2_data'], df_row['phi'])

    # Transversal data
    ax1 = fig.add_subplot(gs0[0, 0])
    ax1.plot(df_row['trZ_time'],new_T,'-k',lw=2,label='HHT')
    ax1.plot(trZ_signal_time,tr2,c='gray',ls='--',lw=1,label='HHE')
    ax1.axvspan(xmin=signal_window_start, xmax=signal_window_final, ymin=0, ymax=1,facecolor='none', edgecolor='blue', linestyle='--', lw=2,alpha=0.25)
    ax1.annotate(df_row['network']+'.'+df_row['station']+'..HHT', (0.95, 0.85),xycoords='axes fraction',fontsize=15, va='center',ha='right',bbox=dict(boxstyle="round", fc="white"))
    ax1.set_xlim(-TIME_WINDOW,TIME_WINDOW)
    ax1.tick_params(axis="x", labelbottom=False)
    ax1.grid(which='major',linestyle=':')
    ax1.legend(loc='lower left')

    # Radial data
    ax2 = fig.add_subplot(gs0[1, 0], sharex=ax1, sharey=ax1)
    ax2.plot(df_row['trZ_time'],new_R,'-k',label='HHR')
    ax2.plot(trZ_signal_time,tr1,c='gray',ls='--',lw=1,label='HHN')
    ax2.axvspan(xmin=signal_window_start, xmax=signal_window_final, ymin=0, ymax=1,facecolor='none', edgecolor='blue', linestyle='--', lw=2,alpha=0.25)
    ax2.annotate(df_row['network']+'.'+df_row['station']+'..HHR', (0.95, 0.85),xycoords='axes fraction',fontsize=15, va='center',ha='right',bbox=dict(boxstyle="round", fc="white"))
    ax2.tick_params(axis="x", labelbottom=False)
    ax2.grid(which='major',linestyle=':')
    ax2.legend(loc='lower left')

    # Vertical data and noise and signal window
    ax3 = fig.add_subplot(gs0[2, 0], sharex=ax1, sharey=ax1)
    ax3.plot(df_row['trZ_time'],df_row['trZ_data'],'-k')
    ax3.tick_params(axis="x", labelbottom=False)
    ax3.annotate(df_row['network']+'.'+df_row['station']+'..HHZ', (0.95, 0.85),xycoords='axes fraction',fontsize=15, va='center',ha='right',bbox=dict(boxstyle="round", fc="white"))
    ax3.axvspan(xmin=signal_window_start, xmax=signal_window_final, ymin=0, ymax=1,facecolor='none', edgecolor='blue', linestyle='--', lw=2,alpha=0.25,label='signal')
    ax3.axvspan(xmin=noise_window_start, xmax=noise_window_final, ymin=0, ymax=1,facecolor='none', edgecolor='red', linestyle='--', lw=2,alpha=0.25,label='noise')
    ax3.grid(which='major',linestyle=':')
    ax3.legend(loc='lower left')

    # Vertical data AIC curve
    ax4 = fig.add_subplot(gs0[3, 0], sharex=ax1)
    ax4.plot(df_row['trZ_time'],aic_curve, 'k')
    ax4.scatter(time_P_arr,amp_P_arr, marker='v',s=100,c='k',lw=1,ec='r',label='changepoint')
    ax4.annotate('AIC', (0.95, 0.85),xycoords='axes fraction',fontsize=15, va='center',ha='right',bbox=dict(boxstyle="round", fc="white"))
    ax4.set_xlabel('Timelag (s)',fontsize=15)
    ax4.grid(which='major',linestyle=':')                          
    ax4.legend(loc='lower left')
    ax4.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax4.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    
    # --------------------
    # Search Space of BAZ

    # Step size for the azimuth search (in degrees).
    dphi = 0.1

    # Array of azimuth angles to search through (in degrees).
    ang = np.arange(0., 360., dphi)
    
    # --------------------  
    # Transversal signal strength
    
    ax5 = fig.add_subplot(gs1[0, 0])
    ax5.plot(ang,df_row['signal_strength'],'.k')
    ax5.plot(df_row['phi'],df_row['SS_best'],'*r',ms=10)
    ax5.set_ylim(0,1)
    ax5.set_xlim(0,360)
    ax5.tick_params(axis="both", which='both',labelbottom=False, labelright=True, labelleft=True, labeltop=False,bottom=True, top=True, left=True, right=True)
    ax5.set_title(r'$SS_{T}$',fontsize=15)
    ax5.grid(which='major',linestyle=':')                          
                                
    # Similarity between vertical and radial
    ax6 = fig.add_subplot(gs1[1, 0],sharex=ax5)
    ax6.plot(ang,df_row['similarity_vertical_radial'],'.k')
    ax6.plot(df_row['phi'],df_row['SZR_best'],'*r',ms=10)
    ax6.set_ylim(-1,1)
    ax6.tick_params(axis="both", which='both',labelbottom=False, labelright=True, labelleft=True, labeltop=False,bottom=True, top=True, left=True, right=True)
    ax6.set_title(r'$CC_{RZ}$',fontsize=15)
    ax6.grid(which='major',linestyle=':')                          

    # Transverse-to-Radial Energy Ratio
    ax7 = fig.add_subplot(gs1[2, 0],sharex=ax5)
    ax7.plot(ang,df_row['energy_transverse_radial'],'.',c='k')
    ax7.plot(df_row['phi'],df_row['ERTR_best'],'*r',ms=10)
    ax7.tick_params(axis="both", which='both',labelbottom=False, labelright=True, labelleft=True, labeltop=False,bottom=True, top=True, left=True, right=True)
    ax7.set_title(r'$E_{T}/E_{R}$',fontsize=15)
    ax7.grid(which='major',linestyle=':')                          
    ax7.yaxis.label.set_color('k')
                                                                
    # Radial-to-Vertical Energy Ratio
    ax8 = fig.add_subplot(gs1[3, 0],sharex=ax5)
    ax8.plot(ang,df_row['energy_radial_vertical'],'.',c='k')
    ax8.plot(df_row['phi'],df_row['ERRZ_best'],'*r',ms=10)
    ax8.set_title(r'$E_{R}/E_{Z}$',fontsize=15)
    ax8.set_xlabel('Orientation Angle (deg)',fontsize=15)
    ax8.grid(which='major',linestyle=':')                          
    ax8.tick_params(axis="both", which='both',labelbottom=True, labelright=True, labelleft=True, labeltop=False,bottom=True, top=True, left=True, right=True)
    ax8.yaxis.label.set_color('k')

    # --------------------------
    # Adding global location map

    ax_map = plt.axes([0.025, 0.76, 0.12, 0.12], projection=ccrs.Orthographic(central_latitude=df_row['stla'],central_longitude=df_row['stlo']))
    ax_map.set_global()

    # ---------------------
    # Adding background map 

    ax_map.add_feature(cfeature.LAND)
    ax_map.add_feature(cfeature.OCEAN)
    ax_map.add_feature(cfeature.COASTLINE)
                            
    ax_map.scatter(df_row['evlo'],df_row['evla'],color="y",marker='*',s=200,ec='k',transform=ccrs.PlateCarree())
    ax_map.scatter(df_row['stlo'],df_row['stla'],color="r",marker='^',s=50,transform=ccrs.PlateCarree())
    ax_map.plot([df_row['stlo'], df_row['evlo']], [df_row['stla'], df_row['evla']], c='gray',ls='-',lw=2, transform=ccrs.Geodetic())
   
    # ===================================================================================
    # focal mechanism (https://docs.obspy.org/tutorial/code_snippets/beachball_plot.html)
    # ===================================================================================
                                    
    # ---------------------------
    # Plotting: adding a new axes
                                    
    newax = fig.add_axes([-0.06, 0.34, 0.3,  0.3])
    
    # -----------------------------------------
    # Computing: Retrieving moment tensor info
                                            
    mt = df_row['moment tensor'] 
    
    # -----------------------------------------------------------------------------------------------------------------------------------------
    # Plotting: graphical representation of a focal mechanism (https://docs.obspy.org/packages/autogen/obspy.imaging.beachball.beachball.html)

    # Normalize event depth values between 0 and 600 km:
    min_val = 0
    max_val = 600
    normalized_values = [(x - min_val) / (max_val - min_val) for x in np.arange(min_val, max_val,10)]

    # Colormap "Plasma" for each value
    colors = [plt.cm.Spectral(value) for value in normalized_values]
                                                                        
    # Convert colors RGB to hexadecimal:
    hex_colors = [mcolors.rgb2hex(color) for color in colors]

    # Find the color for a given depth
    diff_ev_depth = [np.abs(numero - df_row['evdp']) for numero in np.arange(min_val, max_val,10)]
                                        
    # Find the min index for a given depth
    index_min_ev_depth = diff_ev_depth.index(min(diff_ev_depth))

    # Plotting the hexcolor
    bball = beach(fm=mt, xy=(0, 0.5),size=200, width=0.75, facecolor=hex_colors[index_min_ev_depth])
        
    # -------------------------
    # Plotting: axes parameters 
                                
    newax.add_collection(bball)
    newax.set_xlim(-1, 1)
    newax.set_ylim(-1, 1)
    newax.set_aspect('equal')
    newax.axis('off')
        
    # ===========================================================
    # ray paths (https://docs.obspy.org/packages/obspy.taup.html)
    # ===========================================================

    # ---------------------------------------------------------------------------------------------------
    # Computing: The paths travelled by the rays to the receiver for a given phase and 1D velocity model 
    
    model = TauPyModel(model="iasp91")
    arrivals_ray_path = model.get_ray_paths(source_depth_in_km=df_row['evdp'], distance_in_degree=df_row['gcarc'], phase_list=['P','PKP','PKIKP'])

    # -------------------------
    # Plotting: axes parameters 
                                    
    ax_raypath = fig.add_axes([0.022, 0.24, 0.13,  0.13], projection='polar')
    arrivals_ray_path.plot_rays(ax=ax_raypath)
        
    # ==========================================
    
    output_figure_ORIENTATION = ORIENTATION_OUTPUT+'ORIENTATION_FIGURES/EARTHQUAKES/'+df_row['network']+'.'+df_row['station']+'/'
    os.makedirs(output_figure_ORIENTATION,exist_ok=True)
    fig.savefig(output_figure_ORIENTATION+'ORIENTATION_'+df_row['station']+'_'+df_row['evname']+'_'+df_row['quality']+'.png',dpi=100)
    plt.close()
# -------------------

def plotting_station_event_histogram(station_df,ORIENTATION_OUTPUT=ORIENTATION_OUTPUT):
    
    # Create figure:
    fig = plt.figure(figsize=(15,10))
    gs = gridspec.GridSpec(1,1)
    
    # Create map plot:
    ax1 = fig.add_subplot(gs[:], projection=ccrs.Mollweide())

    # Create histogram insets:
    ax2 = inset_axes(ax1, width=2, height=0.75,bbox_to_anchor=(0.2, 1.),bbox_transform=ax1.transAxes, loc="center", borderpad=0)
    ax3 = inset_axes(ax1, width=2, height=0.75,bbox_to_anchor=(0.4, 1.),bbox_transform=ax1.transAxes, loc="center", borderpad=0)
    ax4 = inset_axes(ax1, width=2, height=0.75,bbox_to_anchor=(0.6, 1.),bbox_transform=ax1.transAxes, loc="center", borderpad=0)
    ax5 = inset_axes(ax1, width=2, height=0.75,bbox_to_anchor=(0.8, 1.),bbox_transform=ax1.transAxes, loc="center", borderpad=0)
    
    # Generate evenly spaced values between 0 and 1 for the colormap:
    colors = plt.cm.nipy_spectral(np.linspace(0, 1, len(station_df['station'].unique())))
    
    # Create a mapping from station to color:
    station_color_map = dict(zip(station_df['station'].unique(), colors))

    # Loop over each station:
    for sta in station_df['station'].unique():
        df_sta = station_df[station_df['station'] == sta]
        cs = station_color_map[sta]
    
        # letter a):
        ax1.text(0.05,0.9,'a)', fontsize=14, verticalalignment='center', horizontalalignment='center',transform=ax1.transAxes)
    
        # Plotting stations:
        for lon, lat in zip(df_sta['stlo'].unique(),df_sta['stla'].unique()):
        	ax1.plot(lon, lat, '^',markersize=10,markeredgecolor='k',markerfacecolor=cs, transform=ccrs.Geodetic())
        
        # Use the cartopy interface to create a matplotlib transform object
        # for the Geodetic coordinate system. We will use this along with
        # matplotlib's offset_copy function to define a coordinate system which
        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax1)
        text_transform = offset_copy(geodetic_transform, units='dots', x=5,y=50)
    
        # Plotting stations names:
        for lon, lat, net_n,sta_n in zip(df_sta['stlo'].unique(),df_sta['stla'].unique(),df_sta['network'].unique(),df_sta['station'].unique()):
            ax1.text(lon, lat,net_n+'.'+sta_n, verticalalignment='center', horizontalalignment='center',transform=text_transform,bbox=dict(facecolor='w', alpha=0.5, boxstyle='round'))
    
        # Plotting earthquakes:
        for lon, lat in zip(df_sta['evlo'].values,df_sta['evla'].values):
        	ax1.plot(lon, lat, '*',markersize=6,markeredgecolor='k',markerfacecolor=cs, transform=ccrs.Geodetic(),alpha=0.5)
    
        # draw coastlines and borders:
        ax1.stock_img()
        ax1.add_feature(cfeature.LAND)
        ax1.add_feature(cfeature.COASTLINE)
        ax1.add_feature(cfeature.BORDERS, lw=0.5)
        
        #############
        # Histogram of distance:
        ax2.hist(df_sta['gcarc'].values,bins=50,orientation='vertical',color=cs,alpha=0.5)
        ax2.set_title("DIST",y=0.5)
        ax2.text(0.1,0.85,'b)', fontsize=14, verticalalignment='center', horizontalalignment='center',transform=ax2.transAxes)
        ax2.tick_params(axis="x", which='both', labelbottom=False, labeltop=True,top=True, rotation=30)
        ax2.set_ylim(0,200)
    
        #############
        # Histogram of signal-to-noise:
        ax3.hist(df_sta['SNR'].values,bins=50,orientation='vertical',color=cs,alpha=0.5)
        ax3.set_title("SNR",y=0.5)
        ax3.text(0.1,0.85,'c)', fontsize=14, verticalalignment='center', horizontalalignment='center',transform=ax3.transAxes)
        ax3.tick_params(axis="x", which='both', labelbottom=False, labeltop=True,top=True, rotation=30)
        ax3.set_ylim(0,200)
        
        #############
        # Histogram of magnitude:
        ax4.hist(df_sta['evmag'].values,bins=50,orientation='vertical',color=cs,alpha=0.5) 
        ax4.set_title("MAG",y=0.5)
        ax4.set_xlim(5.5,9)
        ax4.set_ylim(0,200)
        ax4.text(0.1,0.85,'d)', fontsize=14, verticalalignment='center', horizontalalignment='center',transform=ax4.transAxes)
        ax4.tick_params(axis="x", which='both', labelbottom=False, labeltop=True,top=True, rotation=30)
    
        #############
        # Histogram of time (year):
        ax5.hist(df_sta['evtime'].dt.year,bins=10,orientation='vertical',color=cs,alpha=0.5)
        ax5.set_title("YEAR",y=0.5)
        ax5.text(0.1,0.85,'e)', fontsize=14, verticalalignment='center', horizontalalignment='center',transform=ax5.transAxes)
        ax5.tick_params(axis="x", which='both', labelbottom=False, labeltop=True,top=True, rotation=30)
        ax5.set_ylim(0,200)
        
        plt.tight_layout()
        
        # Saving figure
        output_figure_ORIENTATION = ORIENTATION_OUTPUT + 'ORIENTATION_FIGURES/'
        os.makedirs(output_figure_ORIENTATION, exist_ok=True)
        fig.savefig(output_figure_ORIENTATION + f'LOCATION_STATIONS.png',facecolor='w',dpi=300,pad_inches=0.1)
        plt.close()

def classification_plot_N_Z_ratio(df_sta,ORIENTATION_OUTPUT=ORIENTATION_OUTPUT)

    # Create colors for each earthquake source
    classes = ['N','N-SS','SS-N','SS','SS-R','R-SS','R']
    colors = [mcolors.to_rgba(plt.cm.RdYlBu(each),alpha=0.5) for each in np.linspace(0, 1, len(classes))]
    color_map = dict(zip(classes, colors))
    
    # Create figure
    fig, axes = plt.subplots(2,4, figsize=(10, 5),sharex=True,sharey=True)
    axes = axes.flatten()
    
    # Subplot for each class
    for i in range(len(classes)):
        axes[i].set_title(classes[i])
    
        df_sta_class = df_sta[df_sta['event_class'] == classes[i]]
        ratio = df_sta_class['gain_HHN'] / df_sta_class['gain_HHZ']
        axes[i].hist(ratio, bins=100, color='k', edgecolor='k', alpha=0.75)
        axes[i].set_xlim(0,5)
    
    # Exclude last axis
    axes[-1].axis('off')
    
    # Final adjust
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    # Saving figure
    output_figure_CLASS = ORIENTATION_OUTPUT + 'EVENT_CLASS_FIGURES/'
    os.makedirs(output_figure_CLASS, exist_ok=True)
    fig.savefig(output_figure_CLASS + f'CLASS_HISTOGRAM_RZ_TOTAL.png',facecolor='w',dpi=300)