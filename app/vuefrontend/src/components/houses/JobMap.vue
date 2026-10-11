<template>
  <JRPage>
    <JRPageHeader title="Communities Map" />

    <div class="jr-job-map__filters">
      <JRField
        v-slot="{ describedby }"
        label="First community"
        inputId="jr-map-first">
        <JRSelect
          v-model="firstCommunityId"
          inputId="jr-map-first"
          :options="optionsExcept(secondCommunityId)"
          optionLabel="name"
          optionValue="id"
          placeholder="Select a community"
          filter
          showClear
          :disabled="loading || loadError"
          :ariaDescribedby="describedby" />
      </JRField>
      <JRField
        v-slot="{ describedby }"
        label="Second community"
        inputId="jr-map-second">
        <JRSelect
          v-model="secondCommunityId"
          inputId="jr-map-second"
          :options="optionsExcept(firstCommunityId)"
          optionLabel="name"
          optionValue="id"
          placeholder="Select a community"
          filter
          showClear
          :disabled="loading || loadError"
          :ariaDescribedby="describedby" />
      </JRField>
    </div>

    <p v-if="loading" class="jr-job-map__status" role="status">
      Loading communities…
    </p>
    <p v-else-if="loadError" class="jr-job-map__status" role="alert">
      Could not load communities. Refresh the page and try again.
    </p>
    <p
      v-else
      :class="hasMeasuredDistance ? 'jr-job-map__distance' : 'jr-job-map__status'"
      role="status">
      {{ distanceMessage }}
    </p>

    <div ref="mapEl" class="jr-job-map" role="region" aria-label="Communities map"></div>
  </JRPage>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import axios from 'axios';
import mapIconUrl from '@assets/map-icon.png';
import { JRField, JRPage, JRPageHeader, JRSelect } from '@/ui';

const EARTH_RADIUS_MILES = 3958.7613;

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function coordsOf(job) {
  if (!job || job.latitude == null || job.longitude == null) return null;
  if (job.latitude === '' || job.longitude === '') return null;
  const lat = Number(job.latitude);
  const lng = Number(job.longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  return [lat, lng];
}

function milesBetween(a, b) {
  const toRad = (deg) => (deg * Math.PI) / 180;
  const dLat = toRad(b[0] - a[0]);
  const dLng = toRad(b[1] - a[1]);
  const lat1 = toRad(a[0]);
  const lat2 = toRad(b[0]);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
  return 2 * EARTH_RADIUS_MILES * Math.asin(Math.min(1, Math.sqrt(h)));
}

function formatMiles(miles) {
  return `${miles.toFixed(1)} miles`;
}

export default {
  name: 'JobMap',
  components: { JRField, JRPage, JRPageHeader, JRSelect },
  data() {
    return {
      map: null,
      jobs: [],
      markers: [],
      routeLayer: null,
      firstCommunityId: null,
      secondCommunityId: null,
      loading: true,
      loadError: false,
      _resizeListener: null,
    };
  },
  computed: {
    communityOptions() {
      return [...this.jobs].sort((a, b) =>
        String(a.name || '').localeCompare(String(b.name || ''))
      );
    },
    firstJob() {
      return this.jobById(this.firstCommunityId);
    },
    secondJob() {
      return this.jobById(this.secondCommunityId);
    },
    hasMeasuredDistance() {
      return !!(coordsOf(this.firstJob) && coordsOf(this.secondJob));
    },
    distanceMessage() {
      const first = this.firstJob;
      const second = this.secondJob;
      if (!first && !second) {
        return 'Select two communities to measure the distance between them.';
      }
      if (!first || !second) {
        return 'Select a second community to measure the distance.';
      }
      const from = coordsOf(first);
      const to = coordsOf(second);
      if (!from && !to) {
        return 'Neither community has a map location, so the distance cannot be measured.';
      }
      if (!from) {
        return `${first.name} has no map location, so the distance cannot be measured.`;
      }
      if (!to) {
        return `${second.name} has no map location, so the distance cannot be measured.`;
      }
      const miles = milesBetween(from, to);
      if (miles < 0.05) {
        return `${first.name} and ${second.name} share the same map location.`;
      }
      return `${first.name} and ${second.name} are ${formatMiles(miles)} apart.`;
    },
  },
  watch: {
    firstCommunityId(id) {
      if (id != null && id === this.secondCommunityId) {
        this.secondCommunityId = null;
        return;
      }
      this.syncMap();
    },
    secondCommunityId(id) {
      if (id != null && id === this.firstCommunityId) {
        this.secondCommunityId = null;
        return;
      }
      this.syncMap();
    },
  },
  methods: {
    jobById(id) {
      if (id == null) return null;
      return this.jobs.find((job) => job.id === id) || null;
    },
    optionsExcept(excludeId) {
      if (excludeId == null) return this.communityOptions;
      return this.communityOptions.filter((job) => job.id !== excludeId);
    },
    async fetchJobs() {
      this.loading = true;
      this.loadError = false;
      try {
        const response = await axios.get('/api/job/');
        const data = response.data;
        this.jobs = Array.isArray(data) ? data : data?.results || [];
        this.syncMap();
      } catch (error) {
        console.error('Error fetching jobs:', error);
        this.jobs = [];
        this.loadError = true;
      } finally {
        this.loading = false;
      }
    },
    createIcon() {
      return L.icon({
        iconUrl: mapIconUrl,
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
      });
    },
    createLabel(jobName) {
      return L.divIcon({
        className: 'jr-job-map__label',
        html: `<span>${escapeHtml(jobName)}</span>`,
        iconAnchor: [0, -8],
      });
    },
    jobsOnMap() {
      const selected = [this.firstJob, this.secondJob].filter(Boolean);
      const source = selected.length ? selected : this.jobs;
      return source.filter((job) => coordsOf(job));
    },
    clearRoute() {
      if (this.routeLayer && this.map) {
        this.map.removeLayer(this.routeLayer);
      }
      this.routeLayer = null;
    },
    drawRoute() {
      this.clearRoute();
      const from = coordsOf(this.firstJob);
      const to = coordsOf(this.secondJob);
      if (!this.map || !from || !to) return;
      const miles = milesBetween(from, to);
      const color =
        getComputedStyle(this.$refs.mapEl).getPropertyValue('--color-jr-primary').trim() ||
        'rgb(37, 99, 235)';
      const line = L.polyline([from, to], {
        color,
        weight: 3,
        opacity: 1,
      });
      if (miles >= 0.05) {
        line.bindTooltip(formatMiles(miles), {
          permanent: true,
          direction: 'center',
          className: 'jr-job-map__miles',
        });
      }
      line.addTo(this.map);
      this.routeLayer = line;
    },
    addMarkers() {
      if (!this.map || !this.map._loaded) return;

      this.markers.forEach((marker) => {
        if (this.map.hasLayer(marker)) {
          this.map.removeLayer(marker);
        }
      });
      this.markers = [];

      this.jobsOnMap().forEach((job) => {
        const point = coordsOf(job);
        const marker = L.marker(point, { icon: this.createIcon() });
        const leaders = Array.isArray(job.crew_leaders) ? job.crew_leaders : [];
        const crewLeaders = leaders.length
          ? leaders.map(escapeHtml).join(', ')
          : 'No crew assigned';
        const popupContent = `<b>${escapeHtml(job.name || '')}</b><br>${escapeHtml(job.address || 'No address provided')}<br><b>Crew:</b> ${crewLeaders}`;
        marker.bindPopup(popupContent);
        marker.addTo(this.map);

        const label = L.marker(point, {
          icon: this.createLabel(job.name || ''),
          interactive: false,
        }).addTo(this.map);

        this.markers.push(marker, label);
      });
    },
    fitMap() {
      if (!this.map || !this.map._loaded) return;
      const points = this.jobsOnMap().map((job) => coordsOf(job));
      if (!points.length) {
        this.map.setView([37.0902, -95.7129], 4);
        return;
      }
      if (points.length === 1) {
        this.map.setView(points[0], 13);
        return;
      }
      const bounds = L.latLngBounds(points);
      if (bounds.isValid()) {
        this.map.fitBounds(bounds, { padding: [48, 48] });
      }
    },
    syncMap() {
      if (!this.map || !this.map._loaded) return;
      this.addMarkers();
      this.drawRoute();
      this.fitMap();
    },
  },
  mounted() {
    this.map = L.map(this.$refs.mapEl, {
      zoomAnimation: false,
      markerZoomAnimation: false,
      fadeAnimation: false,
    }).setView([37.0902, -95.7129], 4);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
    }).addTo(this.map);

    this.map.whenReady(() => {
      this.fetchJobs();
    });

    const resizeListener = () => {
      if (this.map && this.map._loaded) this.map.invalidateSize();
    };
    window.addEventListener('resize', resizeListener);
    this._resizeListener = resizeListener;
  },
  beforeUnmount() {
    if (this.map) {
      this.map.off();
      this.map.remove();
      this.map = null;
    }
    if (this._resizeListener) {
      window.removeEventListener('resize', this._resizeListener);
      this._resizeListener = null;
    }
  },
};
</script>

<style scoped>
.jr-job-map__filters {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.jr-job-map__status {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-jr-muted);
}

.jr-job-map__distance {
  margin: 0 0 0.75rem;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--color-jr-text);
}

.jr-job-map {
  width: 100%;
  height: 55vh;
  min-height: 18rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  overflow: hidden;
}

@media (min-width: 768px) {
  .jr-job-map__filters {
    grid-template-columns: 1fr 1fr;
  }

  .jr-job-map {
    height: 70vh;
  }
}

:deep(.jr-job-map__label span) {
  display: inline-block;
  padding: 0.15rem 0.35rem;
  background: var(--color-jr-surface);
  color: var(--color-jr-text);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.3;
  white-space: nowrap;
}

:deep(.jr-job-map__miles) {
  padding: 0.2rem 0.4rem;
  background: var(--color-jr-surface);
  color: var(--color-jr-text);
  border: 1px solid var(--color-jr-primary);
  border-radius: var(--radius-jr-control);
  box-shadow: none;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.3;
}
</style>
