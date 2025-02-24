<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results Page</title>
    <link rel="stylesheet" href="./static/css/style.css">
    <link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgo=">
</head>
<body>
    <div class="queryR">
        <form action="" method="post" target="_self">
            <input type="text" class="searchR" name="keywords" placeholder="{{curr_search}}">
            <button type="submit" class="btnR">Search/Next</button>
        </form>
    </div>

    <div class="contents">
        <h1>Page {{page}} results</h1>
        <h1 display="inline-block">
            Your Search Results!
            <img src="./static/assets/logo.png" alt="Logo" width="80px">
        </h1>
        % if not results:
            <p>No search results...</p>
        % else:
        <table id=”results”>
            <tr>
                <td>Word</td>
                <td>Count</td>
            </tr>
            % for item in results:
            <tr>
                <td>{{item}}</td>
                <td>{{results[item]}}</td>
            </tr>
            %end
        </table>
        
        % if not urls:
            <p>No search results...</p>
        % else:
        <table id=”results”>
            <tr>
                <td>URLs</td>
            </tr>
            % for url in urls:
            <tr>
                <td><a href="{{url}}">{{url}}</a></td>
            </tr>
            % end
        </table>
    </div>
    
</body>
</html>