<?php
header("Access-Control-Allow-Origin: *");
// var_dump($_POST['path'])

$pieces = explode("/", $_POST['path']);
$output = "uploads/";

// creates all directories leading to materials
for ($i = 0; $i< count($pieces); $i++) {
    $output .= $pieces[$i] . "/";
    if (!file_exists($output)) {
        $oldmask = umask(0);
        mkdir($output, 0777);
        mkdir($output);  //create directory if not exist
        umask($oldmask);
    }
}

$upload_dir = "uploads/" . $_POST['path'] . "/";
foreach ($_FILES['myFiles']['tmp_name'] as $key => $value) {
    $targetPath = $upload_dir . basename($_FILES['myFiles']['name'][$key]);
    move_uploaded_file($value, $targetPath);
    echo "success";
}
?>

<html>
    <body>
        <img src="https://c.tenor.com/L6KaDFfBRloAAAAC/thanos-the-work-is-done.gif"/>
    </body>
</html>