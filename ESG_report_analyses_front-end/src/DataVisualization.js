import React from 'react';
import { Chart } from 'react-google-charts';

function DataVisualization({ data }) {
  return (
    <div>
      <h3>Data Table:</h3>
      <table border="1">
        <thead>
          <tr>
            {Object.keys(data.csv1[0]).map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.csv1.map((row, index) => (
            <tr key={index}>
              {Object.values(row).map((value, i) => (
                <td key={i}>{value}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Visualization:</h3>
      <Chart
        chartType="Bar"
        data={[
          ['Category', 'Value1', 'Value2'],
          ...data.csv2.map((row) => [row.Column1, parseFloat(row.Column2), parseFloat(row.Column3)]),
        ]}
        options={{
          title: 'CSV Data Visualization',
        }}
        width="100%"
        height="400px"
      />
    </div>
  );
}

export default DataVisualization;