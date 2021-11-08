# streamey
simple nodejs streaming server. Should work on any browser. Let me know if it doesn't!

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
<p>  Example: rickandmorty/season_1/e_1</p>
<p>Right now it only supports videos in .mp4 format.</p>
<p>Put a file named <code>thumbnail.jpeg</code> in the show's directory to have a thumbnail displayed in the front end.</p>
<p>Example: <code>rickandmorty/thumbnail.jpeg</code></p>
