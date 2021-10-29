const express = require("express");
const path = require("path");
const morgan = require('morgan');
const helmet = require("helmet");
const {compile} = require('tempura')
const fs = require("fs");

const app = express();
const PORT = 4200;

app.use(morgan('dev'));
//app.use(helmet())
app.use(express.static(path.join(__dirname, './static')))

const renderPage = async (templatePath, params) =>{
  const template = await fs.readFileSync(templatePath, 'utf8')
  const render = compile(template)

  return (render(params))
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

app.get("/show/:showName", async (req,res) =>{
  //TODO: set up a redis cache so this doesn't have to be done on every request
  const { showName } = req.params;
  const showPath = path.join(__dirname, `./shows/${showName}`);
  const seasons = await fs.readdirSync(showPath);
  const cleanedSeasons = seasons.filter(season => season !== '.DS_Store');
  const seasonsAndEpsiodes = [];
  for (const season of cleanedSeasons){
    const episodesInSeasonPath = path.join(__dirname, `./shows/${showName}/${season}`)
    const episodesInSeason = await fs.readdirSync(episodesInSeasonPath);

    const cleanedEpisodes = episodesInSeason.filter(episode => episode !== '.DS_Store');

    let seasonDisplayName = season.split("_");
    seasonDisplayName[0] = capitalizeFirstLetter(seasonDisplayName[0])
    seasonDisplayName = seasonDisplayName.join(" ");

    const episodes = []
    for(const e of cleanedEpisodes){
      const episode= {}
      episode.file = `/shows/${showName}/${season}/${e}`;
      episode.displayName = e.replace("e_", "Episode ").split(".")[0];
      episodes.push(episode)
    }

    seasonsAndEpsiodes.push({
      displayName: seasonDisplayName,
      episodes
    })
  }

  const templateParams = {
    showName,
    seasonsAndEpsiodes
  }

  const templatePath = path.join(__dirname, './views/episodeList.hbs')
  const template = await renderPage(templatePath, templateParams)
  res.send(template);
})

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

    // Listing 4.
    if (req.method === "HEAD") {
        res.statusCode = 200;
        res.setHeader("accept-ranges", "bytes");
        res.setHeader("content-length", contentLength);
        res.end();
    }
    else {
        // Listing 5.
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

        // Listing 6.
        res.statusCode = start !== undefined || end !== undefined ? 206 : 200;

        res.setHeader("content-length", retrievedLength);

        if (range !== undefined) {
            res.setHeader("content-range", `bytes ${start || 0}-${end || (contentLength-1)}/${contentLength}`);
            res.setHeader("accept-ranges", "bytes");
        }

        // Listing 7.
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

app.get("/", async (req,res) => {
  const showsPath = path.join(__dirname, './shows');
  const shows = await fs.readdirSync(showsPath);
  const cleaned = shows.filter(show => show !== '.DS_Store')
  const templateParams = {
    availableShows : cleaned,
  }

  const templatePath = path.join(__dirname, './views/index.hbs')
  const template = await renderPage(templatePath, templateParams)
  res.send(template);
})

app.listen(PORT, function () {
  console.log(`App is live at http://localhost:${PORT}`);
});