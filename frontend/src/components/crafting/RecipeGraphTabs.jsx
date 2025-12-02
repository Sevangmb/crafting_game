import React, { useMemo, useState } from 'react';
import { Box, Tabs, Tab, Chip, Typography } from '@mui/material';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

// Helpers: classification
const isTool = (name) => {
    const n = (name || '').toLowerCase();
    return [
        'pioche', 'pioche en bronze', 'hache', 'hache en pierre', 'hache en fer',
        'pelle', 'épée', 'couteau', 'canne à pêche', 'arc', 'arc renforcé'
    ].some((k) => n.startsWith(k));
};

const isWorkstationMat = (name) => {
    const n = (name || '').toLowerCase();
    return ['établi', 'étau', 'banc de menuisier', "banc d'archer"].includes(n);
};

const classifyMaterial = (m, allRecipes) => {
    if (!m) return 'autres';
    if (m.is_food) return 'produits_finis';
    if (isTool(m.name)) return 'outils';
    if (isWorkstationMat(m.name)) return 'stations';
    const usedAsIngredient = allRecipes?.some((r) => r.ingredients?.some((ing) => ing.material?.id === m.id));
    const producedByRecipe = allRecipes?.some((r) => r.result_material?.id === m.id);
    if (usedAsIngredient && producedByRecipe) return 'semi_finis';
    if (usedAsIngredient && !producedByRecipe) return 'matieres_premieres';
    if (!usedAsIngredient && producedByRecipe) return 'produits_finis';
    return 'autres';
};

const classifyRecipe = (r) => {
    const res = r?.result_material;
    if (!res) return 'autres';
    if (isWorkstationMat(res.name)) return 'stations';
    if (isTool(res.name)) return 'outils';
    if (res.is_food) return 'produits_finis';
    return 'semi_finis';
};

const tabs = [
    { key: 'tous', label: 'Toutes' },
    { key: 'outils', label: 'Outils' },
    { key: 'stations', label: 'Stations' },
    { key: 'produits_finis', label: 'Produits finis' },
    { key: 'semi_finis', label: 'Semi-finis' },
    { key: 'matieres_premieres', label: 'Matières premières' },
];

export default function RecipeGraphTabs({ recipes }) {
    const [tab, setTab] = useState('tous');

    const { nodes, edges, counts } = useMemo(() => {
        const nodesArr = [];
        const edgesArr = [];
        const nodeIds = new Set();
        const edgeIds = new Set();

        const filteredRecipes = (recipes || []).filter((r) => {
            if (tab === 'tous') return true;
            const rc = classifyRecipe(r);
            if (rc === tab) return true;
            // also show recipes whose result is in a category but allow materials of other categories to appear as context
            return false;
        });

        // Build nodes/edges
        // Simple layout columns: ingredient materials (x=0), recipes (x=400), results (x=800)
        let yIngr = 0, yRec = 0, yRes = 0;
        const stepY = 120;

        const pushNode = (id, data, position) => {
            if (nodeIds.has(id)) return;
            nodeIds.add(id);
            nodesArr.push({ id, data, position, type: 'default' });
        };

        const pushEdge = (id, source, target, label) => {
            if (edgeIds.has(id)) return;
            edgeIds.add(id);
            edgesArr.push({ id, source, target, label, animated: false });
        };

        for (const r of filteredRecipes) {
            const recId = `rec-${r.id}`;
            pushNode(recId, { label: `${r.icon || '🧩'} ${r.name}` }, { x: 400, y: yRec });
            const res = r.result_material;
            if (res) {
                const matId = `mat-${res.id}`;
                pushNode(matId, { label: `${res.icon} ${res.name}` }, { x: 800, y: yRes });
                pushEdge(`${recId}->${matId}`, recId, matId, `x${r.result_quantity}`);
                yRes += stepY;
            }
            if (Array.isArray(r.ingredients)) {
                for (const ing of r.ingredients) {
                    const m = ing.material;
                    if (!m) continue;
                    const mId = `mat-${m.id}`;
                    if (!nodeIds.has(mId)) {
                        pushNode(mId, { label: `${m.icon} ${m.name}` }, { x: 0, y: yIngr });
                        yIngr += stepY;
                    }
                    pushEdge(`${mId}->${recId}`, mId, recId, `x${ing.quantity}`);
                }
            }
            yRec += stepY;
        }

        // Counts for tab badges (deduped)
        const countObj = {
            outils: 0,
            stations: 0,
            produits_finis: 0,
            semi_finis: 0,
            matieres_premieres: 0,
        };
        const matCounted = new Set();
        const recCounted = new Set();
        for (const r of recipes || []) {
            const rc = classifyRecipe(r);
            if (!recCounted.has(r.id)) {
                recCounted.add(r.id);
                if (rc in countObj) countObj[rc] += 1;
            }
            if (r.result_material && !matCounted.has(r.result_material.id)) {
                matCounted.add(r.result_material.id);
            }
            for (const ing of r.ingredients || []) {
                if (ing.material && !matCounted.has(ing.material.id)) {
                    matCounted.add(ing.material.id);
                }
            }
        }

        return { nodes: nodesArr, edges: edgesArr, counts: countObj };
    }, [recipes, tab]);

    return (
        <Box sx={{ height: 520, display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" scrollButtons allowScrollButtonsMobile>
                    {tabs.map((t) => (
                        <Tab
                            key={t.key}
                            value={t.key}
                            label={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography variant="body2">{t.label}</Typography>
                                    {t.key !== 'tous' && (
                                        <Chip size="small" label={counts[t.key] || 0} />
                                    )}
                                </Box>
                            }
                        />
                    ))}
                </Tabs>
            </Box>
            <Box sx={{ flex: 1, borderRadius: 1, overflow: 'hidden' }}>
                <ReactFlow nodes={nodes} edges={edges} fitView>
                    <MiniMap />
                    <Controls />
                    <Background gap={16} />
                </ReactFlow>
            </Box>
        </Box>
    );
}
