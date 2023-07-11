if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside = {
    trigger_hover: function(hoverData) {
        var myPlot = document.getElementById("metrics_graph")
        if (!myPlot.children[1]) {
            return window.dash_clientside.no_update
        }
        myPlot.children[1].id = "metrics_graph_js"

        if (hoverData) {
            if (Array.isArray(hoverData.points[0].customdata)) {
                var t = hoverData.points[0].customdata[0]
            } else {
                var t = hoverData.points[0].customdata
            }
            t = Math.round(t*10)/10
            Plotly.Fx.hover("metrics_graph_js", {xval: t, yval:0})
        }
        return window.dash_clientside.no_update
    }
}