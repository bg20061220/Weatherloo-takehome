# PLan is to make a 2d world map with SST colored by temperature and a time 
# slider to move through 20 snapshots and 
# Using a basic html file to make the visualisation can host it on github pages 
# along with the map will also make a visual conveying the average sst
# by time of day comparing 00:00 vs 06:00 vs 12:00 vs 18:00
# make another visual of a histogram of global sst distribution at each snapshot
# different between first and last snapshot , where the temp changed the most in 120 hours.
# average sst by latitude
# i am also picking the 120 hour to window to start from Dec 20 2006 and then 
# 20 snapshots after that , 20 Dec cause that's my birthday.

import pickle 
import numpy as np 
import plotly .graph_objects as go 
from plotly.subplots import make_subplots 
import plotly.io as pio 

print("loading data")

with open('sst_data.pkl' , 'rb') as f : 
    data = pickle.load(f)

sst = data['sst']
lat = data['lat']
long = data['long']
times = data['time']

n_snapshots = sst.shape[0]

# Taking every fourth data point to make it faster to render 

step = 4
lat_ds = lat[::step] 
lon_ds = long[::step]
sst_ds = sst[: ,  ::step , ::step] 

vmin = -2.6 # min value in the dataset for temp
vmax = 34.6 # max value in the dataset for temp


print("Building main map")

hist_traces = [] # list to store precomputed histogram data for all 20 snapshots
# each entry in hist_traces contains the bin centers , the counts , and the color for the snapshot
colors_hist = [
      '#4361ee','#3a86ff','#48cae4','#90e0ef',
    '#00b4d8','#0096c7','#0077b6','#023e8a',
    '#ade8f4','#caf0f8','#4cc9f0','#4895ef',
    '#560bad','#7209b7','#b5179e','#f72585',
    '#ff6d00','#ff9e00','#ffba08','#ffd60a'
]

# the loop to build the histogram data for each snapshots
for i in range(n_snapshots):
    vals = sst[i].flatten() 
    vals = vals[~np.isnan(vals)]
    counts , bin_edges = np.histogram(vals , bins=60 , range=(vmin , vmax)) 
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2 
    hist_traces.append((bin_centers, counts, colors_hist[i]))

# difference map last- first snapshot
diff = sst_ds[-1] - sst_ds[0]
diff_abs = np.nanmax(np.abs(diff))

# another idea dividing the world in 5 horizontal bands by latitude. Would
# expect tropics to be warmer than the poles. 

bands = [
    ('Polar South (<-60°)',  lat < -60),
    ('Mid South (-60–-30°)', (lat >= -60) & (lat < -30)),
    ('Tropics (-30–30°)',    (lat >= -30) & (lat < 30)),
    ('Mid North (30–60°)',   (lat >= 30)  & (lat < 60)),
    ('Polar North (>60°)',   lat >= 60),
]
band_colors = ['#4361ee', '#48cae4', '#f72585', '#ff9e00', '#7209b7']

band_means = {}
for name , mask in bands : 
    means = []
    for i in range(n_snapshots): 
        vals = sst[i][mask].flatten()
        vals = vals[~np.isnan(vals)]
        means.append(np.mean(vals) if len(vals) > 0 else np.nan)
    band_means[name] = means


# also trying to visualize this by the time of day 

tod_labels = ['00:00', '06:00', '12:00', '18:00']
tod_colors = ['#023e8a', '#4361ee', '#f72585', '#ff9e00']
tod_means  = {label: [] for label in tod_labels}

for i , t in enumerate(times) : 
    hour = t[-5:] 
    vals = sst[i].flatten()
    vals = vals[~np.isnan(vals)]
    m = np.nanmean(vals)
    for label in tod_labels : 
        if hour == label : 
            tod_means[label].append(m)

days = ['Dec 20', 'Dec 21', 'Dec 22', 'Dec 23', 'Dec 24']

print("making the figure")


# Row 1: main map (spans all columns)
# Row 2: panel1 | panel2
# Row 3: panel3 | panel4

fig = make_subplots(
    rows = 3 , cols = 2 , 
    row_heights=[0.5  , 0.25 , 0.25], 
    column_widths= [0.5 , 0.5] , 
    specs = [
        [{"colspan": 2, "type": "heatmap"}, None],
        [{"type": "scatter"},               {"type": "bar"}],
        [{"type": "heatmap"},               {"type": "scatter"}],

    ] , 
    subplot_titles=[
        "" , 
        "Average SST by time of day" , "Global SST distribution(snapshot 1)", 
        "Temperature change : Dec 20  -> Dec 24 (°C)" , "Average SST by latitude band"
    ] , 
    vertical_spacing=0.08 , 
    horizontal_spacing=0.08 , 
)

# main map 

fig.add_trace(
    go.Heatmap(
        z=sst_ds[0],
        x=lon_ds,
        y=lat_ds,
        zmin=vmin,
        zmax=vmax,
        colorscale='RdYlBu_r',
        colorbar=dict(
            title=dict(text="°C", side="right"),
            thickness=12,
            len=0.48,
            y=0.76,
            tickfont=dict(size=10),
        ),
        hovertemplate='Lat: %{y:.1f}°<br>Lon: %{x:.1f}°<br>SST: %{z:.1f}°C<extra></extra>',
        name='SST',
    ),
    row=1, col=1,
)

# row 2 left : time of the day lines
for idx, label in enumerate(tod_labels):
    vals = tod_means[label]
    fig.add_trace(
        go.Scatter(
            x=days[:len(vals)],
            y=vals,
            mode='lines+markers',
            name=f'{label} UTC',
            line=dict(color=tod_colors[idx], width=2),
            marker=dict(size=6),
        ),
        row=2, col=1,
    )


# histogram for snapshot 0 
bc, counts, col = hist_traces[0]
fig.add_trace(
    go.Bar(
        x=bc,
        y=counts,
        marker_color=col,
        name='Distribution',
        showlegend=False,
        hovertemplate='%{x:.1f}°C: %{y} cells<extra></extra>',
    ),
    row=2, col=2,
)

# row 3 : difference map 
fig.add_trace(
    go.Heatmap(
        z=diff,
        x=lon_ds,
        y=lat_ds,
        zmin=-diff_abs,
        zmax=diff_abs,
        colorscale='RdBu_r',
        colorbar=dict(
            title=dict(text="ΔT (°C)", side="right"),
            thickness=12,
            len=0.22,
            y=0.12,
            tickfont=dict(size=10),
        ),
        hovertemplate='Lat: %{y:.1f}°<br>Lon: %{x:.1f}°<br>ΔT: %{z:.2f}°C<extra></extra>',
        name='Δ SST',
        showlegend=False,
    ),
    row=3, col=1,
)
 
# latitude band lines 
for idx, (name, _) in enumerate(bands):
    fig.add_trace(
        go.Scatter(
            x=list(range(n_snapshots)),
            y=band_means[name],
            mode='lines+markers',
            name=name,
            line=dict(color=band_colors[idx], width=2),
            marker=dict(size=5),
            showlegend=True,
        ),
        row=3, col=2,
    )

# slider frames + updating the main map and histogram 
frames = []
for i in range(n_snapshots):
    bc, counts, col = hist_traces[i]
    frame = go.Frame(
        data=[
            go.Heatmap(z=sst_ds[i], x=lon_ds, y=lat_ds, zmin=vmin, zmax=vmax),
            go.Bar(x=bc, y=counts, marker_color=col),
        ],
        traces=[0, 5],   # trace indices to update (main map=0, histogram=5)
        name=str(i),
    )
    frames.append(frame)
 
fig.frames = frames

# slider 
sliders = [dict(
    active=0,
    currentvalue=dict(prefix="Snapshot: ", font=dict(size=13)),
    pad=dict(t=10, b=10),
    steps=[
        dict(
            args=[[str(i)], dict(frame=dict(duration=0, redraw=True), mode='immediate')],
            label=times[i][5:],   # show MM-DD HH:MM
            method='animate',
        )
        for i in range(n_snapshots)
    ],
)]

# layout
fig.update_layout(
    title=dict(
        text='Sea Surface Temperature — ERA5 · Dec 20–24 2006',
        font=dict(size=18, family='Georgia, serif'),
        x=0.5,
    ),
    height=1100,
    paper_bgcolor='#0d1117',
    plot_bgcolor='#0d1117',
    font=dict(color='#e6edf3', family='monospace'),
    sliders=sliders,
    legend=dict(
        bgcolor='rgba(255,255,255,0.05)',
        bordercolor='rgba(255,255,255,0.1)',
        borderwidth=1,
        font=dict(size=11),
    ),
    margin=dict(t=80, b=60, l=60, r=60),
)

for row in range(1, 4):
    for col in range(1, 3):
        try:
            fig.update_xaxes(
                gridcolor='rgba(255,255,255,0.05)',
                zerolinecolor='rgba(255,255,255,0.1)',
                row=row, col=col,
            )
            fig.update_yaxes(
                gridcolor='rgba(255,255,255,0.05)',
                zerolinecolor='rgba(255,255,255,0.1)',
                row=row, col=col,
            )
        except Exception:
            pass


fig.update_xaxes(title_text="Longitude", row=1, col=1)
fig.update_yaxes(title_text="Latitude",  row=1, col=1)
fig.update_xaxes(title_text="Longitude", row=3, col=1)
fig.update_yaxes(title_text="Latitude",  row=3, col=1)
fig.update_xaxes(title_text="Temperature (°C)", row=2, col=2)
fig.update_yaxes(title_text="Grid cells",        row=2, col=2)
fig.update_xaxes(title_text="Day",               row=2, col=1)
fig.update_yaxes(title_text="Mean SST (°C)",     row=2, col=1)
fig.update_xaxes(title_text="Snapshot index",    row=3, col=2)
fig.update_yaxes(title_text="Mean SST (°C)",     row=3, col=2)

# export 
print("Exporting to visualization.html ...")
pio.write_html(fig, file='visualization.html', auto_open=False, include_plotlyjs=True)
print("Done — open visualization.html in your browser")

