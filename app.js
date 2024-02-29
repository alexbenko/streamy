const express = require("express");
const path = require("path");
const morgan = require('morgan');
const fs = require("fs");

const app = express();
const PORT = 4200;

app.use(morgan('dev'));
app.use(express.static(path.join(__dirname, './static')))

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

app.get("/shows/:showName/:season/:episode", async (req, res) => {
  const {showName,season,episode} = req.params;
  const filePath = `/shows/${showName}/${season}/${episode}`;
  const range = req.headers.range
  const options = {};
  let end = undefined
  if (range) {
    const bytesPrefix = "bytes=";
    if (range.startsWith(bytesPrefix)) {
        const bytesRange = range.substring(bytesPrefix.length);
        const parts = bytesRange.split("-");
        if (parts.length === 2) {
            const rangeStart = parts[0] && parts[0].trim();
            if (rangeStart && rangeStart.length > 0) {
                options.start = start = parseInt(rangeStart);
            }
            const rangeEnd = parts[1] && parts[1].trim();
            if (rangeEnd && rangeEnd.length > 0) {
                end = parseInt(rangeEnd);
                options.end = end
            }
        }
    }
  }

  res.setHeader("content-type", "video/mp4");

  fs.stat('.' + filePath, (err, stat) => {
    if (err) {
        console.error(`File stat error for ${filePath}.`);
        console.error(err);
        res.sendStatus(500);
        return;
    }

    let contentLength = stat.size;


    if (req.method === "HEAD") {
        res.statusCode = 200;
        res.setHeader("accept-ranges", "bytes");
        res.setHeader("content-length", contentLength);
        res.end();
    }
    else {

        let retrievedLength;
        if (start !== undefined && end !== undefined) {
            retrievedLength = (end+1) - start;
        }
        else if (start !== undefined) {
            retrievedLength = contentLength - start;
        }
        else if (end !== undefined) {
            retrievedLength = (end+1);
        }
        else {
            retrievedLength = contentLength;
        }

        res.statusCode = start !== undefined || end !== undefined ? 206 : 200;

        res.setHeader("content-length", retrievedLength);

        if (range !== undefined) {
            res.setHeader("content-range", `bytes ${start || 0}-${end || (contentLength-1)}/${contentLength}`);
            res.setHeader("accept-ranges", "bytes");
        }


        const fileStream = fs.createReadStream('.' + filePath, options);
        fileStream.on("error", error => {
            console.log(`Error reading file ${filePath}.`);
            console.log(error);
            res.sendStatus(500);
        });


        fileStream.pipe(res);
    }
  });
})

app.get("/:showname/thumbnail.jpeg", async (req, res)=>{
  const thumbnailPath = path.join(__dirname, `/shows/${req.params.showname}/thumbnail.jpeg`);
  res.sendFile(thumbnailPath);
})

app.get("/shows", async (req, res) => {
  const showsPath = path.join(__dirname, "./shows");
  const shows = await fs.readdirSync(showsPath);
  const cleanedShows = shows.filter(show => !show.includes("."));

  const showsWithSeasonsAndEpisodes = {};

  for (const show of cleanedShows) {
    const showPath = path.join(__dirname, `./shows/${show}`);
    const seasons = await fs.readdirSync(showPath);
    const cleanedSeasons = seasons.filter(season => !season.includes("."));

    const seasonsAndEpisodes = [];
    for (const season of cleanedSeasons) {
      const episodesInSeasonPath = path.join(__dirname, `./shows/${show}/${season}`);
      const episodesInSeason = await fs.readdirSync(episodesInSeasonPath);

      const cleanedEpisodes = episodesInSeason.filter(episode => episode !== '.DS_Store');

      let seasonDisplayName = season.split("_");
      seasonDisplayName[0] = capitalizeFirstLetter(seasonDisplayName[0]);
      seasonDisplayName = seasonDisplayName.join(" ");

      const episodes = [];
      for (const e of cleanedEpisodes) {
        const episode = {};
        episode.file = `/shows/${show}/${season}/${e}`;
        episode.displayName = e.replace("e_", "Episode ").split(".")[0];
        episodes.push(episode);
      }

      seasonsAndEpisodes.push({
        displayName: seasonDisplayName,
        episodes
      });
    }

    showsWithSeasonsAndEpisodes[show] = seasonsAndEpisodes;
  }

  res.send(showsWithSeasonsAndEpisodes);
});

app.listen(PORT, function () {
  console.log(`App is live at http://localhost:${PORT}`);
});