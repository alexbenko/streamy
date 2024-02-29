import { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, Accordion, AccordionSummary, AccordionDetails, Typography, Box, IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CloseIcon from '@mui/icons-material/Close';
import './EpisodeList.css'
interface Episode {
  displayName: string;
  file: string;
}

interface Season {
  displayName: string;
  episodes: Episode[];
}

interface EpisodeListProps {
  showName: string;
  seasonsAndEpisodes: Season[];
  apiRootPath: string
}

const EpisodeList = ({ showName, seasonsAndEpisodes, apiRootPath }: EpisodeListProps) => {
  const [selectedEpisode, setSelectedEpisode] = useState<string | null>('');

  const handleEpisodeClick = (file: string) => {
    setSelectedEpisode(file);
    console.log(file)
  };

  const handleClose = () => {
    setSelectedEpisode(null);
  };

  return (
    <div>
      <h2>{showName}</h2>
      {seasonsAndEpisodes.map((season, index) => (
        <Accordion key={index}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>{season.displayName}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {season.episodes.map((episode, index) => (
              <Typography
                key={index}
                onClick={() => handleEpisodeClick(episode.file)}
                sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
              >
                {episode.displayName}
              </Typography>
            ))}
          </AccordionDetails>
        </Accordion>
      ))}
      <Dialog open={!!selectedEpisode} onClose={handleClose}>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{selectedEpisode}</Typography>
            <IconButton edge="end" color="inherit" onClick={handleClose} aria-label="close">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <video
            src={`${apiRootPath}${selectedEpisode}`}
            style={{ width: '100%' }}
            playsInline autoPlay muted loop controls
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EpisodeList;