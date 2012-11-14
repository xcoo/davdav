<?php
include_once(dirname(__FILE__).'server_config.php');

basic_auth(array("username" => "password"));

$file_path = $_POST["file_path"];

$link = mysql_connect($sql_server,$sql_user,$sql_pw);
if (!$link) {
	die('failed to connect'.mysql_error());
}

mysql_query("SET NAMES utf8",$link);
$db_selected = mysql_select_db($sql_db, $link);
if (!$db_selected){
	die('failed to select database'.mysql_error());
}

$sql="UPDATE thumbnail SET enable = 0 WHERE thumbnail = '$file_path'";

$result = mysql_query($sql);

if (!$result) {
    die('Update query failed'.mysql_error());
}

$close_flag = mysql_close($link);


$pageURL = "http://davdav.uetamasamichi.com";
header('location:'. $pageURL);


function basic_auth($auth_list,$realm="Restricted Area",$failed_text="Don't delete my picture without permission!!!!!"){
    if (isset($_SERVER['PHP_AUTH_USER']) and isset($auth_list[$_SERVER['PHP_AUTH_USER']])){
        if ($auth_list[$_SERVER['PHP_AUTH_USER']] == $_SERVER['PHP_AUTH_PW']){
            return $_SERVER['PHP_AUTH_USER'];
        }
    }
 
    header('WWW-Authenticate: Basic realm="'.$realm.'"');
    header('HTTP/1.0 401 Unauthorized');
    header('Content-type: text/html; charset='.mb_internal_encoding());
 
    die($failed_text);
}
?>

