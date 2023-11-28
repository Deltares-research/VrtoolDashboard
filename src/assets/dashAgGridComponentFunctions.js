var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};


// custom component to display boolean data as a DBC Switch
dagcomponentfuncs.DBC_Switch = function (props) {
    const {setData, value} = props;

    // updated the dbc component
    setProps = ({value}) => {
       // update the grid
        props.node.setDataValue(props.column.colId, value);
        // update to trigger a dash callback
        setData(value)
    }

    return React.createElement(
        window.dash_bootstrap_components.Switch, {
            value: value,
            checked: value,
            setProps,
            style: {"paddingTop": 6},
        }
    )
};
