import React from 'react';
import {Composition} from 'remotion';
import {BotEpisode, botDuration} from './BotSeries';
import EPS1 from './bot_series.json';
import EPS2 from './extra_series.json';
import TL1 from './bot_tl.json';
import TL2 from './extra_tl.json';
import {HostLayer} from './HostLayer';
import HD from './host_demo.json';
import {HostCorner} from './HostCorner';
import HC from './host_corner.json';

// Композиция создаётся автоматически для каждого эпизода, у которого есть озвучка (таймлайн).
// ID: ep-<id>-<RU|EN>, например ep-x1-RU
const ALL = [...(EPS1 as any[]), ...(EPS2 as any[])];
const TL = {...(TL1 as any), ...(TL2 as any)};

export const Root: React.FC = () => (
  <>
    <Composition id="host-corner" component={HostCorner} durationInFrames={Math.round((HC as any).duration * 30)} fps={30} width={1080} height={1920} />
    <Composition id="host-layer" component={HostLayer} durationInFrames={Math.round((HD as any).duration * 30)} fps={30} width={1080} height={1920} />
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
