import React from 'react';
import {Composition} from 'remotion';
import {BotEpisode, botDuration} from './BotSeries';
import EPS1 from './bot_series.json';
import EPS2 from './extra_series.json';
import TL1 from './bot_tl.json';
import TL2 from './extra_tl.json';

// Композиция создаётся автоматически для каждого эпизода, у которого есть озвучка (таймлайн).
// ID: ep-<id>-<RU|EN>, например ep-x1-RU
const ALL = [...(EPS1 as any[]), ...(EPS2 as any[])];
const TL = {...(TL1 as any), ...(TL2 as any)};

export const Root: React.FC = () => (
  <>
    {ALL.filter((e) => TL[e.id]).flatMap((e) =>
      (['ru', 'en'] as const)
        .filter((l) => TL[e.id][l])
        .map((l) => (
          <Composition
            key={`${e.id}-${l}`}
            id={`ep-${e.id}-${l.toUpperCase()}`}
            component={BotEpisode}
            durationInFrames={botDuration(e.id, l)}
            fps={30}
            width={1080}
            height={1920}
            defaultProps={{ep: e.id, lang: l}}
          />
        )),
    )}
  </>
);
