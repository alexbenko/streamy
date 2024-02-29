import { useEffect, useState } from 'react';
import { Card, CardMedia, CardContent, Typography, Dialog, DialogTitle, DialogContent, Container, Grid, IconButton, Box } from '@mui/material';
import CircularProgress from '@mui/material/CircularProgress';
import EpisodeList from '../components/episodeList/EpisodeList';
import CloseIcon from '@mui/icons-material/Close';

const isProduction = import.meta.env.MODE === "production";
const apiRootPath = isProduction ? "" : "/api";

interface Episode {
  displayName: string;
  file: string;
}

interface Season {
  displayName: string;
  episodes: Episode[];
}

interface Show {
  [key: string]: Season[];
}

const Index = () => {
  const [loading, setLoading] = useState(true);
  const [availableShows, setAvailableShows] = useState<Show | null>(null);
  const [selectedShow, setSelectedShow] = useState<string | null>(null);

  useEffect(() => {
    const fetchShows = async () => {
      try {
        const response = await fetch(`${apiRootPath}/shows`);
        const data = await response.json();
        setAvailableShows(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchShows();
  }, []);

  const handleShowClick = (show: string) => {
    setSelectedShow(show);
  };

  const handleClose = () => {
    setSelectedShow(null);
  };

  if (loading || !availableShows) {
    return <CircularProgress />;
  }

  return (
    <Container maxWidth="xl" sx={{ minHeight: "100vh", pl: "0", pr: "0" }}>
      <Grid container spacing={2}>
        {Object.keys(availableShows).map(show => (
          <Grid item xs={12} sm={6} md={3} key={show}>
            <Card
              onClick={() => handleShowClick(show)}
              sx={{
                maxWidth: 350,
                cursor: 'pointer',
                transition: 'transform 0.15s ease-in-out', '&:hover': { transform: 'scale(1.03)' }}}
            >
              <CardMedia
                component="img"

                image={`${apiRootPath}/${show}/thumbnail.jpeg`}
                alt={show}
              />
              <CardContent>
                <Typography variant="h5" component="div">
                  {show}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Dialog open={!!selectedShow} onClose={handleClose} fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{selectedShow}</Typography>
            <IconButton edge="end" color="inherit" onClick={handleClose} aria-label="close">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedShow && availableShows[selectedShow] && (
            <EpisodeList
              apiRootPath={apiRootPath}
              showName={selectedShow}
              seasonsAndEpisodes={availableShows[selectedShow]} />
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default Index;