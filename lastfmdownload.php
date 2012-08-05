#!/usr/bin/php
<?php
// PHP last.fm listening data downloader
$user = "";
$secret = "";
$apikey = "";

function getTracksForPage($page){
	global $user, $secret, $apikey;
	$failcount = 0;
	$done = false;
	$url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user='.$user.'&api_key='.$apikey.'&limit=200&page='.$page;
	
	// Try three times to download the file from last.fm before terminating
	while ($failcount < 3 && !$done) {
		try {
			if ($response = file_get_contents($url)) {
				$xml = simplexml_load_string($response);
				if ($xml['status'] != 'ok') {
					echo "We have a problem for page ".$page."\n";
					echo $response."\n";
					throw new Exception('Invalid response from last.fm');
				}
				$done = true;
			}
			else {
				throw new Exception('Request failed');
			}
		} catch (Exception $e) {
			$failcount++;
			echo $e->getMessage();
			sleep(1);
		}
	}
	if (!$done) {
		echo "Download failed 3 times. Aborting.\n";
		die(102);
	}
	return $response;
}

// Main block
$fh = fopen("lastfmplaytimes.tmp", "w") or die(100);
date_default_timezone_set("Europe/London");
// Get the number of pages and store it in $totalpages
$response = getTracksForPage(1);
$totalpages = preg_match('/totalPages=\"(\d+)\"/', $response, $matches);
if ( count($totalpages) ) {
	$totalpages = $matches[1];
}
else {
	echo("Invalid response from last.fm");
	die(101);
}
$startTime = microtime(true);
// Loop over all pages, and write date and time of plays to tempfile
for ($page = 1; $page <= $totalpages; $page++) {
	$response = getTracksForPage($page);
	$response = explode("\n", $response, -1);
	foreach ($response as $line) {
		preg_match("/uts=\"(\d{10})\"/", $line, $matches);
		if ( count($matches) == 2 ) {
			$time = $matches[1];
			$time = date("Y-m-d-N H:i", $time);
			fwrite($fh, $time."\n");
		}
	}
	
	// Update the screen on progress
	$percentdone = round(($page/$totalpages)*100, 1);
	$currentTime = microtime(true);
	$secsRemaining = (($currentTime-$startTime)/($page/$totalpages)) - ($currentTime-$startTime);
	$minsRemaining = floor($secsRemaining/60);
	$secsRemaining = $secsRemaining % 60;
	$timeRemaining = $minsRemaining."m".$secsRemaining."s";
	echo "\rDownloaded page ".$page."/".$totalpages." (".number_format($percentdone,1)."%), ".$timeRemaining." remaining      ";
}
echo "\nDownload complete\n";
fclose($fh);
// Run the python-based 
$execString = "python heatmap.py ".$user;
exec($execString);
?>
