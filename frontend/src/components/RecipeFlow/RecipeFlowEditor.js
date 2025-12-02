import React, { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Box } from '@mui/material';
import MaterialNode from './MaterialNode';
import RecipeNode from './RecipeNode';
import dagre from 'dagre';

const nodeTypes = {
  material: MaterialNode,
  recipe: RecipeNode,
};

// Layout automatique avec dagre
const getLayoutedElements = (nodes, edges) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: 'LR', ranksep: 150, nodesep: 100 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: node.width || 200, height: node.height || 100 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - (node.width || 200) / 2,
        y: nodeWithPosition.y - (node.height || 100) / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

// Générer le graphe depuis les recettes
const generateGraphFromRecipes = (recipes) => {
  const nodes = [];
  const edges = [];
  const materialMap = new Map();
  let nodeId = 0;

  recipes.forEach((recipe) => {
    // Créer le node de recette
    const recipeNodeId = `recipe-${recipe.id}`;
    nodes.push({
      id: recipeNodeId,
      type: 'recipe',
      data: {
        name: recipe.name,
        icon: recipe.icon,
        description: recipe.description,
        requiredWorkstation: recipe.required_workstation,
      },
      width: 200,
      height: 150,
    });

    // Créer les nodes pour les ingrédients
    recipe.ingredients?.forEach((ingredient) => {
      const materialId = `material-${ingredient.material.id}`;

      // Créer le node du matériau s'il n'existe pas
      if (!materialMap.has(materialId)) {
        nodes.push({
          id: materialId,
          type: 'material',
          data: {
            name: ingredient.material.name,
            icon: ingredient.material.icon,
            rarity: ingredient.material.rarity,
          },
          width: 180,
          height: 120,
        });
        materialMap.set(materialId, true);
      }

      // Créer l'edge matériau -> recette
      edges.push({
        id: `edge-${nodeId++}`,
        source: materialId,
        target: recipeNodeId,
        label: `x${ingredient.quantity}`,
        animated: true,
        style: { stroke: '#2196f3', strokeWidth: 2 },
      });
    });

    // Créer le node pour le résultat
    const resultMaterialId = `material-${recipe.result_material.id}`;
    if (!materialMap.has(resultMaterialId)) {
      nodes.push({
        id: resultMaterialId,
        type: 'material',
        data: {
          name: recipe.result_material.name,
          icon: recipe.result_material.icon,
          rarity: recipe.result_material.rarity,
          quantity: recipe.result_quantity,
        },
        width: 180,
        height: 120,
      });
      materialMap.set(resultMaterialId, true);
    }

    // Créer l'edge recette -> résultat
    edges.push({
      id: `edge-${nodeId++}`,
      source: recipeNodeId,
      target: resultMaterialId,
      label: `x${recipe.result_quantity}`,
      animated: true,
      style: { stroke: '#4caf50', strokeWidth: 3 },
    });
  });

  return getLayoutedElements(nodes, edges);
};

const RecipeFlowEditor = ({ recipes }) => {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => generateGraphFromRecipes(recipes || []),
    [recipes]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <Box sx={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Background color="#aaa" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'recipe') return '#ff9800';
            return '#2196f3';
          }}
        />
      </ReactFlow>
    </Box>
  );
};

export default RecipeFlowEditor;
