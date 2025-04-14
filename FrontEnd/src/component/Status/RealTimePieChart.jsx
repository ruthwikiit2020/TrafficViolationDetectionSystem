import * as React from "react";
import { PieChart } from "@mui/x-charts";

// Data for the pie chart
export default function RealTimePieChart({violationsData}) {
  return (
    <div style={{ width: 500, height: 400}}>
      <PieChart
         margin={{ top: 100, bottom: 20, left: 130, right:10 }}
        series={[
          {
            data: violationsData,
            highlightScope: { faded: "global" },
            faded: { innerRadius: 30, additionalRadius: -20, color: 'gray' },
            valueFormatter: (data) => `${data.value} violations`, // Formatting the displayed value
            
          },
        ]}
        width={400}
        height={400}
        legend={{
          labelStyle: {
            fontSize: 14,
            fill: 'white',
            padding:10,
          },
          // direction: 'row',
          position: { vertical: 'top', horizontal: 'right' },
          padding: 0,
        }}
      />
    </div>
  );
}
