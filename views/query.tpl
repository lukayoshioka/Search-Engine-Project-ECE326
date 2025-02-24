<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">    
    <link rel="stylesheet" href="./static/css/style.css">
    <link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgo=">
    <title>Query Page</title>
</head>

<body>
    <div class="header">
        % if email == "":
            <a href="/auth">Sign In</a>
        % else:
            <div class="profile">
                <img src="{{picture}}"></img>
                <p>{{name}}</p>
                <a href="/logout"> Sign Out </a>
            </div>
        % end
    </div>
    <div class="title">
        <h1 display="inline-block">
            Welcome to AniRec Search Engine!
            <img src="./static/assets/logo.png" alt="Logo" width="80px">
        </h1>
        
    </div>
    <div class="query">
        <form action="" method="post" target="_self">
            <input type="text" class="search" name="keywords" placeholder="Enter Search Here">
            <button type="submit" class="btn">Submit</button>
        </form>
    </div>
    % if email != "":
        <div class="history">
            <p>Top Recent Searches</p>
            % if len(history) == 0:
                <p>Nothing to see here...</p>
            % else:
            <table id="history">
                <tr>
                    <td>Word</td>
                    <td>Count</td>
                </tr>
            % for word in history:
                <tr>
                    <td>{{word}}</td>
                    <td>{{history[word]}}</td>
                </tr>
            % end
            </table>
        </div.>
    % end
</body>
</html>