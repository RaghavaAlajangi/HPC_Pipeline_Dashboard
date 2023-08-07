async function getServerData(request) {
    response = await fetch("/hpc-pipelines/api/serverData", {
        "method": "POST", "body": JSON.stringify(request),
        "headers": {"content-type": "application/json"}
    })
    return response.json()
}


function createServerSideDatasource() {
    return {
        getRows: async (params) => {
            console.log("ServerSideDatasource.getRows: params = ", params);
            var allRows = await getServerData(params.request)
            var request = params.request;
            var doingInfinite = request.startRow != null && request.endRow != null;
            var result = doingInfinite
                ? {
                    rowData: allRows.slice(request.startRow, request.endRow),
                    rowCount: allRows.length,
                }
                : {rowData: allRows};
            console.log("getRows: result = ", result);
            setTimeout(function () {
                params.success(result);
            }, 200);
        },
    };
}
