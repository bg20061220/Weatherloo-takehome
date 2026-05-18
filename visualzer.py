import pickle
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import json

print("Loading data...")
with open('sst_data.pkl', 'rb') as f:
    data = pickle.load(f)

sst   = data['sst']
lat   = data['lat']
lon   = data['long']
times = data['time']

n_snapshots = sst.shape[0]

vmin = -2.6
vmax = 34.6

# Downsample for performance
step   = 4
lat_ds = lat[::step]
lon_ds = lon[::step]
sst_ds = sst[:, ::step, ::step]

print("Building figure...")

colorbar_cfg = dict(
    title=dict(
        text="Sea Surface Temperature (°C)",
        side="right",
        font=dict(size=13, family="Georgia, serif", color="#e6edf3"),
    ),
    thickness=18,
    len=0.85,
    x=1.02,
    tickvals=[-2, 0, 5, 10, 15, 20, 25, 30, 34],
    ticktext=["-2°C", "0°C", "5°C", "10°C", "15°C", "20°C", "25°C", "30°C", "34°C"],
    tickfont=dict(size=12, color="#e6edf3"),
    outlinecolor="rgba(255,255,255,0.15)",
    outlinewidth=1,
    bgcolor="rgba(255,255,255,0.04)",
)

fig = go.Figure()

# Add one trace per snapshot — all share same colorbar, only first visible
for i in range(n_snapshots):
    fig.add_trace(
        go.Heatmap(
            z=sst_ds[i],
            x=lon_ds,
            y=lat_ds,
            zmin=vmin,
            zmax=vmax,
            colorscale='RdYlBu_r',
            visible=(i == 0),
            colorbar=colorbar_cfg,
            showscale=True,
            hovertemplate='Lat: %{y:.1f}°<br>Lon: %{x:.1f}°<br>SST: %{z:.1f}°C<extra></extra>',
            name='',
        )
    )

# Slider steps — toggle visibility + update title
steps = []
for i in range(n_snapshots):
    visibility = [False] * n_snapshots
    visibility[i] = True
    step = dict(
        method='update',
        label=times[i][5:].replace('T', ' '),
        args=[
            {'visible': visibility},
            {'title': {
                'text': f"Sea Surface Temperature — ERA5 &nbsp;·&nbsp; {times[i].replace('T', '  ')} UTC",
                'font': dict(size=20, family="Georgia, serif", color="#e6edf3"),
                'x': 0.5,
                'xanchor': 'center',
            }}
        ],
    )
    steps.append(step)

sliders = [dict(
    active=0,
    pad=dict(t=20, b=10, l=20, r=20),
    bgcolor="rgba(255,255,255,0.06)",
    bordercolor="rgba(255,255,255,0.12)",
    borderwidth=1,
    tickcolor="rgba(255,255,255,0.3)",
    font=dict(color="#e6edf3", size=11),
    currentvalue=dict(visible=False),
    steps=steps,
)]

fig.update_layout(
    title=dict(
        text=f"Sea Surface Temperature — ERA5 &nbsp;·&nbsp; {times[0].replace('T', '  ')} UTC",
        font=dict(size=20, family="Georgia, serif", color="#e6edf3"),
        x=0.5,
        xanchor='center',
        y=0.97,
    ),
    height=700,
    paper_bgcolor='#0d1117',
    plot_bgcolor='#161b22',
    font=dict(color='#e6edf3', family='monospace'),
    sliders=sliders,
    updatemenus=[],
    margin=dict(t=80, b=80, l=60, r=120),
    xaxis=dict(
        title=dict(text="Longitude", font=dict(size=12)),
        gridcolor='rgba(255,255,255,0.05)',
        zerolinecolor='rgba(255,255,255,0.08)',
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        title=dict(text="Latitude", font=dict(size=12)),
        gridcolor='rgba(255,255,255,0.05)',
        zerolinecolor='rgba(255,255,255,0.08)',
        tickfont=dict(size=11),
    ),
)

print("Exporting to visualization.html...")
pio.write_html(fig, file='visualization.html', auto_open=False, include_plotlyjs=True)

# ── Inject pin feature ────────────────────────────────────────────────────────
lat_list = lat_ds.tolist()
lon_list = lon_ds.tolist()
sst_list = sst_ds.tolist()

with open('visualization.html', 'r', encoding='utf-8') as f:
    html = f.read()

injection = f"""
<script>
var SST_DATA = {json.dumps(sst_list)};
var LAT_DATA = {json.dumps(lat_list)};
var LON_DATA = {json.dumps(lon_list)};
var TIMES    = {json.dumps(times)};

var currentSnapshot = 0;
var pinLat = null;
var pinLon = null;

function nearestIndex(arr, val) {{
    var best = 0;
    var bestDist = Math.abs(arr[0] - val);
    for (var i = 1; i < arr.length; i++) {{
        var d = Math.abs(arr[i] - val);
        if (d < bestDist) {{ bestDist = d; best = i; }}
    }}
    return best;
}}

function getSSTAtPin(snapshot, lat, lon) {{
    var li  = nearestIndex(LAT_DATA, lat);
    var loi = nearestIndex(LON_DATA, lon);
    return SST_DATA[snapshot][li][loi];
}}

function dropPin(lat, lon) {{
    var gd = document.getElementsByClassName('plotly-graph-div')[0];

    // Remove existing pin
    for (var i = 0; i < gd.data.length; i++) {{
        if (gd.data[i].name === '__pin__') {{
            Plotly.deleteTraces(gd, i);
            break;
        }}
    }}

    var sst = getSSTAtPin(currentSnapshot, lat, lon);
    var sstText = (sst === null || isNaN(sst)) ? 'No ocean data' : sst.toFixed(2) + '°C';

    Plotly.addTraces(gd, {{
        type: 'scatter',
        mode: 'markers+text',
        x: [lon],
        y: [lat],
        text: [lat.toFixed(2) + '°, ' + lon.toFixed(2) + '° — ' + sstText],
        textposition: 'top center',
        textfont: {{ color: '#ffffff', size: 12, family: 'monospace' }},
        marker: {{
            symbol: 'circle',
            size: 14,
            color: '#f72585',
            line: {{ color: '#ffffff', width: 2 }}
        }},
        name: '__pin__',
        showlegend: false,
        hovertemplate: 'Lat: ' + lat.toFixed(2) + '°<br>Lon: ' + lon.toFixed(2) + '°<br>SST: ' + sstText + '<extra>📍 Pin</extra>',
    }});

    document.getElementById('pin-info').innerText = 'SST at pin: ' + sstText;
}}

document.addEventListener('DOMContentLoaded', function() {{

    // Build panel
    var panel = document.createElement('div');
     panel.style.cssText = `
        position: fixed; top: 16px; right: 20px;
        background: rgba(13,17,23,0.92);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 10px; padding: 10px 14px;
        font-family: monospace; color: #e6edf3;
        z-index: 9999; box-shadow: 0 4px 24px rgba(0,0,0,0.5);
        display: flex; align-items: center; gap: 10px;
    `;

   panel.innerHTML = `
        <div style="font-size:13px; opacity:0.7;">📍</div>
        <input id="inp-lat" type="text" placeholder="Lat" style="
            width:90px; padding:5px 8px;
            background:#161b22; border:1px solid rgba(255,255,255,0.15);
            border-radius:6px; color:#e6edf3; font-family:monospace; font-size:12px;">
        <input id="inp-lon" type="text" placeholder="Lon" style="
            width:90px; padding:5px 8px;
            background:#161b22; border:1px solid rgba(255,255,255,0.15);
            border-radius:6px; color:#e6edf3; font-family:monospace; font-size:12px;">
        <button id="pin-btn" style="
            padding:5px 12px; background:#238636; border:none;
            border-radius:6px; color:#fff; font-family:monospace;
            font-size:12px; cursor:pointer;">Drop</button>
        <button id="clear-btn" style="
            padding:5px 12px; background:#b91c1c; border:none;
            border-radius:6px; color:#fff; font-family:monospace;
            font-size:12px; cursor:pointer;">Clear</button>
        <div id="pin-info" style="font-size:11px; opacity:0.6; white-space:nowrap;"></div>
    `;

    document.body.appendChild(panel);

    // Drop pin on button click
    document.getElementById('pin-btn').addEventListener('click', function() {{
        var lat  = parseFloat(document.getElementById('inp-lat').value.trim());
        var lon  = parseFloat(document.getElementById('inp-lon').value.trim());
        var info = document.getElementById('pin-info');

        if (isNaN(lat) || isNaN(lon)) {{
            info.innerText = 'Enter valid lat and lon.'; return;
        }}
        

        pinLat = lat;
        pinLon = lon;
        dropPin(lat, lon);
    }});

    // Clear pin on button click
    document.getElementById('clear-btn').addEventListener('click', function() {{
        var gd = document.getElementsByClassName('plotly-graph-div')[0];
        for (var i = 0; i < gd.data.length; i++) {{
            if (gd.data[i].name === '__pin__') {{
                Plotly.deleteTraces(gd, i);
                break;
            }}
        }}
        pinLat = null;
        pinLon = null;
        document.getElementById('pin-info').innerText = 'Pin cleared.';
    }});

    // Re-drop pin with updated SST on slider change
    var gd = document.getElementsByClassName('plotly-graph-div')[0];
    gd.on('plotly_sliderchange', function(e) {{
        // Find which trace is now visible
        for (var i = 0; i < gd.data.length; i++) {{
            if (gd.data[i].visible === true && gd.data[i].name !== '__pin__') {{
                currentSnapshot = i; break;
            }}
        }}
        if (pinLat !== null && pinLon !== null) {{
            dropPin(pinLat, pinLon);
        }}
    }});
}});
</script>
"""

html = html.replace('</body>', injection + '</body>')

with open('visualization.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — open visualization.html in your browser")