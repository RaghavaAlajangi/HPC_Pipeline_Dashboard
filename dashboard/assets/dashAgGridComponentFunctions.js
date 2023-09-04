var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.CustomLoadingOverlayForShow = function (props) {
    return React.createElement(
        'div',
        {
            style: {
                border: '1pt solid grey',
                color: props.color || 'grey',
                padding: 10,
            },
        },
        props.loadingMessage
    );
}

dagcomponentfuncs.CustomLoadingOverlayForHSM = function (props) {
    return React.createElement(
        'div',
        {
            style: {
                border: '1pt solid grey',
                color: props.color || 'grey',
                padding: 10,
            },
        },
        props.loadingMessage
    );
}