<?php
  // 时间：2022-08-29
  // 功能：获取24小时内参数的最大最小平均值

  // 跨域解决
  header("Content-type:text/json;charset=UTF-8");
  // header("Access-Control-Allow-Origin:*");
  include 'mysql.php';
  
  date_default_timezone_set('PRC');
  $nowTime = date("Y-m-d H:i:s");
  $oneDayBeforeTime = date("Y-m-d H:i:s",strtotime("-1 day"));
  
  // var_dump($nowTime);
  // var_dump($oneDayBeforeTime);

  $dataName = ['c1', 'c2', 'c3', 'c4', 'c6', 'c5', 'c7'];
  $result = [];
  
  for($i=0; $i<count($dataName); $i++){
    if($dataName[$i] != 'c7'){
      $sql = "SELECT ROUND(AVG($dataName[$i]),2 ) AS avgVal,ROUND(MAX($dataName[$i]),2 ) AS maxVal,ROUND(MIN($dataName[$i]),2 ) AS minVal FROM `table_shuizhi` WHERE times >= '$oneDayBeforeTime' and times <= '$nowTime'";
      $temp = $conn->query($sql)->fetch_array(MYSQLI_ASSOC);
      $temp['name'] = $dataName[$i];
      array_push($result,$temp);
    }else{
      $sql = "SELECT ROUND(AVG($dataName[$i]),2 ) AS avgVal,ROUND(MAX($dataName[$i]),2 ) AS maxVal,ROUND(MIN($dataName[$i]),2 ) AS minVal FROM `table_yelvsu` WHERE times >= '$oneDayBeforeTime' and times <= '$nowTime'";
      $temp = $conn->query($sql)->fetch_array(MYSQLI_ASSOC);
      $temp['name'] = $dataName[$i];
      array_push($result,$temp);
    }
  }

  echo json_encode($result);
  // 7.关闭数据库
  $conn->close();