# streamey
simple nodejs streaming server. Should work on any browser. Let me know if it doesn't! This is not meant for production, I use this on my local network.
MAJOR ISSUES: Found out the html server side template library I used does not support nested loops. So for now it can only display one season. 
<ol>  Steps to set up:
  <li>Ensure nodejs and npm is installed</li>
  <li>Clone the repository: <code>git clone https://github.com/alexbenko/streamy.git</code></li>
  <li><code>cd streamy</code></li>
  <li><code>npm install</code></li>
  <li><code>mkdir shows</code></li>
</ol>

<p>
  In the shows directory follow this layout. showname/season_#/e_#
</p>
<p>  Example: <code>rickandmorty/season_1/e_1</code></p>
<p>Right now it only supports videos in .mp4 format.</p>
<p>Put a file named <code>thumbnail.jpeg</code> in the show's directory to have a thumbnail displayed in the front end.</p>
<p>Example: <code>rickandmorty/thumbnail.jpeg</code></p>
