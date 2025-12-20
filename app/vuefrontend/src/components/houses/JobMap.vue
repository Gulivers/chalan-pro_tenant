<template>
    <div>
        <div id="search-container">
            <input type="text" v-model="searchQuery" placeholder="Search by name, community..." @input="filterJobs" />
        </div>
        <div id="map" style="height: 700px; width: 100%;"></div>
    </div>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import axios from "axios";

export default {
    name: "JobMap",
    data() {
        return {
            map: null,
            jobs: [],
            filteredJobs: [],
            markers: [],
            searchQuery: "",
            _resizeListener: null, // Listener para el evento de redimensionado
        };
    },
    methods: {
        async fetchJobs() {
            try {
                const response = await axios.get("/api/job/");
                this.jobs = response.data;
                this.filteredJobs = [...this.jobs];
                this.addMarkers();
                this.fitMapToJobs();
            } catch (error) {
                console.error("Error fetching jobs:", error);
            }
        },
        createIcon() {
            return L.icon({
                iconUrl: require("@assets/map-icon.png"),
                iconSize: [30, 30],
                iconAnchor: [15, 30],
                popupAnchor: [0, -30],
            });
        },
        createLabel(jobName) {
            return L.divIcon({
                className: "job-label", // CSS personalizado para etiquetas
                html: `<span>${jobName}</span>`,
                iconAnchor: [15, -10], // Ajusta la posición relativa del texto
            });
        },
        addMarkers() {
            if (!this.map || !this.map._loaded) return;

            this.markers.forEach((marker) => {
                if (this.map.hasLayer(marker)) {
                    this.map.removeLayer(marker);
                }
            });
            this.markers = [];

            this.filteredJobs.forEach((job) => {
                if (job.latitude && job.longitude) {
                    const marker = L.marker([job.latitude, job.longitude], {
                        icon: this.createIcon(),
                    });

                    const crewLeaders = job.crew_leaders.length ? job.crew_leaders.join(", ") : "No Crew Assigned";
                    const popupContent = `<b>${job.name}</b><br> ${job.address || "No address provided"}<br> <b>Crew Leader(s):</b> ${crewLeaders} `;
                    marker.bindPopup(popupContent).on("popupclose", (e) => {
                        if (!this.map || !this.map.hasLayer(e.target)) {
                            e.target.unbindPopup();
                        }
                    });
                    marker.addTo(this.map);

                    const label = L.marker([job.latitude, job.longitude], {
                        icon: this.createLabel(job.name),
                        interactive: false,
                    }).addTo(this.map);

                    this.markers.push(marker);
                    this.markers.push(label);
                }
            });
        },
        fitMapToJobs() {
            if (!this.map || !this.map._loaded || this.filteredJobs.length === 0)
                return;

            const bounds = L.latLngBounds(
                this.filteredJobs
                    .filter((job) => job.latitude && job.longitude)
                    .map((job) => [job.latitude, job.longitude])
            );

            if (bounds.isValid()) {
                this.map.fitBounds(bounds, { padding: [20, 20] });
            }
        },
        filterJobs() {
            const query = this.searchQuery.toLowerCase();

            this.filteredJobs = this.jobs.filter((job) => {
                const name = job.name?.toLowerCase() || "";
                const builder =
                    typeof job.builder === "string"
                        ? job.builder.toLowerCase()
                        : job.builder?.name?.toLowerCase() || "";
                const region = job.region?.toLowerCase() || "";

                return (
                    name.includes(query) || builder.includes(query) || region.includes(query)
                );
            });

            this.addMarkers();
            this.fitMapToJobs();
        },
    },
    mounted() {
        this.map = L.map("map", {
            zoomAnimation: false, // Deshabilitar animación de zoom
            markerZoomAnimation: false, // Deshabilitar animación en marcadores
            fadeAnimation: false, // Deshabilitar desvanecimiento en capas
        }).setView([37.0902, -95.7129], 4);

        this.map.whenReady(() => {
            this.fetchJobs();
        });

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors",
        }).addTo(this.map);

        const resizeListener = () => {
            if (this.map && this.map._loaded) this.map.invalidateSize();
        };
        window.addEventListener("resize", resizeListener);
        this._resizeListener = resizeListener;
    },
    beforeUnmount() {
        if (this.map) {
            this.map.eachLayer((layer) => {
                this.map.removeLayer(layer);
            });
            this.map.off();
            this.map.remove();
            this.map = null;
        }
        if (this._resizeListener) {
            window.removeEventListener("resize", this._resizeListener);
            this._resizeListener = null;
        }
    },
};
</script>

<style>
#map {
    height: 80vh;
}

#search-container {
    display: flex;
    justify-content: center;
    margin: 10px 0;
}

#search-container input {
    width: 90%;
    max-width: 500px;
    padding: 10px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

/* Estilo personalizado para las etiquetas */
.job-label span {
    background: white;
    color: black;
    padding: 2px 5px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-size: 12px;
    font-weight: bold;
    white-space: nowrap;
}
</style>