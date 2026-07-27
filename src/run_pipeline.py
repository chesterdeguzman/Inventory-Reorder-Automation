from pathlib import Path
import pandas as pd, numpy as np, matplotlib.pyplot as plt, json
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data/inventory_history.csv',parse_dates=['date'])
summary=df.groupby('sku').agg(avg_daily_demand=('units_demanded','mean'),demand_std=('units_demanded','std'),lead_time_days=('lead_time_days','max'),current_stock=('current_stock','max'),unit_cost=('unit_cost','max'),service_level=('service_level','max')).reset_index()
z=summary.service_level.map({.90:1.282,.95:1.645,.98:2.054}).fillna(1.645)
summary['safety_stock']=z*summary.demand_std*np.sqrt(summary.lead_time_days)
summary['reorder_point']=summary.avg_daily_demand*summary.lead_time_days+summary.safety_stock
summary['recommended_order_qty']=np.maximum(0,np.ceil(summary.reorder_point*1.5-summary.current_stock))
summary['reorder_now']=summary.current_stock<=summary.reorder_point
summary['estimated_order_value']=summary.recommended_order_qty*summary.unit_cost
summary.sort_values(['reorder_now','estimated_order_value'],ascending=[False,False]).to_csv(ROOT/'outputs/reorder_recommendations.csv',index=False)
metrics={'skus_reviewed':int(len(summary)),'skus_to_reorder':int(summary.reorder_now.sum()),'estimated_purchase_value':float(summary.loc[summary.reorder_now,'estimated_order_value'].sum())}
(ROOT/'outputs/metrics.json').write_text(json.dumps(metrics,indent=2))
summary.assign(status=np.where(summary.reorder_now,'Reorder','Sufficient')).status.value_counts().plot(kind='bar',title='Automated Inventory Status'); plt.ylabel('SKUs'); plt.tight_layout(); plt.savefig(ROOT/'images/inventory_status.png',dpi=160); plt.close()
print(metrics)
