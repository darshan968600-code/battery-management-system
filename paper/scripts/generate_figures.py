import matplotlib.pyplot as plt
import numpy as np
import os
from fleet_data import NASA_DATASETS

# Set publication style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8.5
plt.rcParams['ytick.labelsize'] = 8.5
plt.rcParams['legend.fontsize'] = 8.5
plt.rcParams['figure.titlesize'] = 11

os.makedirs('figures', exist_ok=True)

# -------------------------------------------------------------
# FIGURE 1: NASA Ames PCoE Lithium-ion Battery Degradation Suite
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(8.5, 6.2), dpi=300)

colors = {'B0005': '#1f77b4', 'B0006': '#d62728', 'B0007': '#2ca02c', 'B0018': '#ff7f0e'}
markers = {'B0005': 'o', 'B0006': 's', 'B0007': '^', 'B0018': 'D'}

# (a) Capacity Fade vs Cycles
ax1 = axes[0, 0]
for cid, d in NASA_DATASETS.items():
    ax1.plot(d['cycles'], d['capacity_ah'], label=f"Cell {cid}", color=colors[cid], 
             marker=markers[cid], markersize=4, linewidth=1.5, alpha=0.9)
ax1.axhline(y=1.4, color='gray', linestyle='--', linewidth=1, label='EOL Threshold (70%)')
ax1.set_xlabel('Discharge Cycles')
ax1.set_ylabel('Discharge Capacity (Ah)')
ax1.set_title('(a) Capacity Degradation Trajectory (168 Cycles)')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(loc='lower left', framealpha=0.9)

# (b) SOH Capacity Retention Ratio
ax2 = axes[0, 1]
for cid, d in NASA_DATASETS.items():
    soh = [c / d['nominal_ah'] * 100 for c in d['capacity_ah']]
    ax2.plot(d['cycles'], soh, label=f"Cell {cid}", color=colors[cid], 
             marker=markers[cid], markersize=4, linewidth=1.5, alpha=0.9)
ax2.axhline(y=85.0, color='#2ca02c', linestyle=':', linewidth=1.2, label='Normal Limit (85%)')
ax2.axhline(y=70.0, color='#d62728', linestyle='--', linewidth=1.2, label='Degraded Limit (70%)')
ax2.set_xlabel('Discharge Cycles')
ax2.set_ylabel('State of Health SOH (%)')
ax2.set_title('(b) SOH Retention & Decision Boundaries')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(loc='lower left', framealpha=0.9)

# (c) Dynamic Voltage Discharge Profiles across Lifetime (Cell B0005)
ax3 = axes[1, 0]
b5 = NASA_DATASETS['B0005']
timesteps = list(range(1, 33))
ax3.plot(timesteps, b5['discharge_cycle_1'], label='Cycle 1 (Fresh)', color='#2ca02c', linewidth=1.8)
ax3.plot(timesteps, b5['discharge_cycle_80'], label='Cycle 80 (Mid-Life)', color='#ff7f0e', linewidth=1.8, linestyle='--')
ax3.plot(timesteps, b5['discharge_cycle_160'], label='Cycle 160 (Aged)', color='#d62728', linewidth=1.8, linestyle=':')
ax3.set_xlabel('Discharge Time Step (32-Step Window)')
ax3.set_ylabel('Cell Terminal Voltage (V)')
ax3.set_title('(c) Dynamic Discharge Voltage Collapse (Cell B0005)')
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.legend(loc='lower left', framealpha=0.9)

# (d) Surface Temperature Elevation during Discharge (Cell B0005 & B0006)
ax4 = axes[1, 1]
b6 = NASA_DATASETS['B0006']
ax4.plot(timesteps, b5['temp_rise_cycle_1'], label='B0005 Cycle 1', color='#1f77b4', linewidth=1.6)
ax4.plot(timesteps, b5['temp_rise_cycle_160'], label='B0005 Cycle 160', color='#1f77b4', linewidth=1.6, linestyle='--')
ax4.plot(timesteps, b6['temp_rise_cycle_1'], label='B0006 Cycle 1', color='#d62728', linewidth=1.6)
ax4.plot(timesteps, b6['temp_rise_cycle_160'], label='B0006 Cycle 160', color='#d62728', linewidth=1.6, linestyle='--')
ax4.set_xlabel('Discharge Time Step (32-Step Window)')
ax4.set_ylabel('Surface Temperature (°C)')
ax4.set_title('(d) Thermal Escalation During Severe Cycling')
ax4.grid(True, linestyle=':', alpha=0.6)
ax4.legend(loc='upper left', framealpha=0.9)

plt.tight_layout()
fig_path = os.path.join('figures', 'fig2_nasa_degradation.png')
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"Generated: {fig_path}")

# -------------------------------------------------------------
# FIGURE 2: Multi-Fleet Digital Twin Distribution Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=300)

fleets = [
    "Urban EV Taxi Fleet\n(35 Packs, NASA B0005)",
    "Heavy Logistics Highway\n(40 Packs, NASA B0006)",
    "Grid Energy Storage\n(45 Packs, NASA B0007)",
    "Airport Ground Support\n(30 Packs, NASA B0018)",
    "Commercial Delivery\n(50 Packs, Composite)"
]
pack_counts = [35, 40, 45, 30, 50]
colors_fleet = ['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd']

bars = ax.bar(fleets, pack_counts, color=colors_fleet, width=0.55, edgecolor='black', linewidth=0.8, alpha=0.85)

for bar, count in zip(bars, pack_counts):
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f"{count} Packs\n({count/200*100:.1f}%)", 
            ha='center', va='bottom', fontsize=8.5, fontweight='bold')

ax.set_ylabel('Monitored Battery Pack Count')
ax.set_title('Operational Fleet Distribution in Cloud Digital Twin (200 Simulated Packs Total)', pad=15)
ax.set_ylim(0, 62)
ax.grid(axis='y', linestyle=':', alpha=0.7)

plt.tight_layout()
fig_fleet = os.path.join('figures', 'fig4_fleet_distribution.png')
plt.savefig(fig_fleet, dpi=300)
plt.close()
print(f"Generated: {fig_fleet}")
