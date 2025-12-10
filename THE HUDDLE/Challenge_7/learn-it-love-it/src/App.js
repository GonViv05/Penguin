import React, { useState, useEffect } from 'react';
import { ThumbsUp, Plus, Edit2, Trash2, X, Save, Link2 } from 'lucide-react';

// Modelo - Gestión de datos
const DataModel = {
  topics: [],
  
  initializeData() {
    const stored = localStorage.getItem('learningTopics');
    if (stored) {
      this.topics = JSON.parse(stored);
    } else {
      this.topics = [
        {
          id: 1,
          title: 'Cómo programar como un ninja',
          description: 'Aprende las técnicas avanzadas de programación',
          votes: 15,
          links: [
            { id: 1, url: 'https://javascript.info', title: 'JavaScript.info', votes: 10 },
            { id: 2, url: 'https://developer.mozilla.org', title: 'MDN Web Docs', votes: 8 }
          ]
        },
        {
          id: 2,
          title: 'Dominar el arte de preparar café',
          description: 'Conviértete en un barista experto',
          votes: 12,
          links: [
            { id: 1, url: 'https://coffeeguide.com', title: 'Coffee Guide', votes: 5 }
          ]
        }
      ];
      this.saveData();
    }
    return this.topics;
  },
  
  saveData() {
    localStorage.setItem('learningTopics', JSON.stringify(this.topics));
  },
  
  getTopics() {
    return [...this.topics].sort((a, b) => b.votes - a.votes);
  },
  
  addTopic(topic) {
    const newTopic = {
      id: Date.now(),
      ...topic,
      votes: 0,
      links: []
    };
    this.topics.push(newTopic);
    this.saveData();
    return newTopic;
  },
  
  updateTopic(id, updates) {
    const index = this.topics.findIndex(t => t.id === id);
    if (index !== -1) {
      this.topics[index] = { ...this.topics[index], ...updates };
      this.saveData();
      return this.topics[index];
    }
    return null;
  },
  
  deleteTopic(id) {
    this.topics = this.topics.filter(t => t.id !== id);
    this.saveData();
  },
  
  voteTopic(id) {
    const topic = this.topics.find(t => t.id === id);
    if (topic) {
      topic.votes++;
      this.saveData();
      return topic;
    }
    return null;
  },
  
  addLink(topicId, link) {
    const topic = this.topics.find(t => t.id === topicId);
    if (topic) {
      const newLink = {
        id: Date.now(),
        ...link,
        votes: 0
      };
      topic.links.push(newLink);
      this.saveData();
      return newLink;
    }
    return null;
  },
  
  updateLink(topicId, linkId, updates) {
    const topic = this.topics.find(t => t.id === topicId);
    if (topic) {
      const linkIndex = topic.links.findIndex(l => l.id === linkId);
      if (linkIndex !== -1) {
        topic.links[linkIndex] = { ...topic.links[linkIndex], ...updates };
        this.saveData();
        return topic.links[linkIndex];
      }
    }
    return null;
  },
  
  deleteLink(topicId, linkId) {
    const topic = this.topics.find(t => t.id === topicId);
    if (topic) {
      topic.links = topic.links.filter(l => l.id !== linkId);
      this.saveData();
    }
  },
  
  voteLink(topicId, linkId) {
    const topic = this.topics.find(t => t.id === topicId);
    if (topic) {
      const link = topic.links.find(l => l.id === linkId);
      if (link) {
        link.votes++;
        this.saveData();
        return link;
      }
    }
    return null;
  }
};

// Componente principal
export default function LearnItLoveItApp() {
  const [topics, setTopics] = useState([]);
  const [showAddTopic, setShowAddTopic] = useState(false);
  const [editingTopic, setEditingTopic] = useState(null);
  const [addingLinkTo, setAddingLinkTo] = useState(null);
  const [editingLink, setEditingLink] = useState(null);
  
  const [newTopicTitle, setNewTopicTitle] = useState('');
  const [newTopicDesc, setNewTopicDesc] = useState('');
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [newLinkTitle, setNewLinkTitle] = useState('');
  const [newLinkUrl, setNewLinkUrl] = useState('');
  const [editLinkTitle, setEditLinkTitle] = useState('');
  const [editLinkUrl, setEditLinkUrl] = useState('');
  
  useEffect(() => {
    loadTopics();
  }, []);
  
  const loadTopics = () => {
    DataModel.initializeData();
    setTopics(DataModel.getTopics());
  };
  
  const handleAddTopic = () => {
    if (!newTopicTitle.trim() || !newTopicDesc.trim()) return;
    DataModel.addTopic({
      title: newTopicTitle,
      description: newTopicDesc
    });
    setTopics(DataModel.getTopics());
    setShowAddTopic(false);
    setNewTopicTitle('');
    setNewTopicDesc('');
  };
  
  const handleUpdateTopic = () => {
    if (!editTitle.trim() || !editDesc.trim()) return;
    DataModel.updateTopic(editingTopic.id, {
      title: editTitle,
      description: editDesc
    });
    setTopics(DataModel.getTopics());
    setEditingTopic(null);
  };
  
  const handleDeleteTopic = (id) => {
    if (window.confirm('¿Estás seguro de eliminar este tema?')) {
      DataModel.deleteTopic(id);
      setTopics(DataModel.getTopics());
    }
  };
  
  const handleVoteTopic = (id) => {
    DataModel.voteTopic(id);
    setTopics(DataModel.getTopics());
  };
  
  const handleAddLink = () => {
    if (!newLinkTitle.trim() || !newLinkUrl.trim()) return;
    DataModel.addLink(addingLinkTo, {
      url: newLinkUrl,
      title: newLinkTitle
    });
    setTopics(DataModel.getTopics());
    setAddingLinkTo(null);
    setNewLinkTitle('');
    setNewLinkUrl('');
  };
  
  const handleUpdateLink = () => {
    if (!editLinkTitle.trim() || !editLinkUrl.trim()) return;
    DataModel.updateLink(editingLink.topicId, editingLink.id, {
      url: editLinkUrl,
      title: editLinkTitle
    });
    setTopics(DataModel.getTopics());
    setEditingLink(null);
  };
  
  const handleDeleteLink = (topicId, linkId) => {
    if (window.confirm('¿Estás seguro de eliminar este enlace?')) {
      DataModel.deleteLink(topicId, linkId);
      setTopics(DataModel.getTopics());
    }
  };
  
  const handleVoteLink = (topicId, linkId) => {
    DataModel.voteLink(topicId, linkId);
    setTopics(DataModel.getTopics());
  };
  
  const startEditTopic = (topic) => {
    setEditingTopic(topic);
    setEditTitle(topic.title);
    setEditDesc(topic.description);
  };
  
  const startEditLink = (link, topicId) => {
    setEditingLink({ ...link, topicId });
    setEditLinkTitle(link.title);
    setEditLinkUrl(link.url);
  };

  return (
    <div className="app-container">
      <div className="container">
        <div className="header">
          <h1 className="title">Learn It, Love It 📚</h1>
          <p className="subtitle">
            Descubre y vota por los mejores temas de aprendizaje
          </p>
        </div>

        <div className="text-center mb-4">
          <button
            onClick={() => setShowAddTopic(true)}
            className="btn btn-primary"
          >
            <Plus size={20} />
            Agregar Nuevo Tema
          </button>
        </div>

        {showAddTopic && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h2 className="modal-title">Nuevo Tema</h2>
                <button 
                  onClick={() => setShowAddTopic(false)}
                  className="btn btn-secondary"
                  style={{ padding: '0.5rem' }}
                >
                  <X size={20} />
                </button>
              </div>
              <div>
                <div className="form-group">
                  <label className="form-label">Título</label>
                  <input
                    type="text"
                    value={newTopicTitle}
                    onChange={(e) => setNewTopicTitle(e.target.value)}
                    className="form-input"
                    placeholder="Ej: Programar como un ninja"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Descripción</label>
                  <textarea
                    value={newTopicDesc}
                    onChange={(e) => setNewTopicDesc(e.target.value)}
                    rows="3"
                    className="form-input"
                    placeholder="Describe el tema..."
                  />
                </div>
                <div className="form-actions">
                  <button
                    onClick={() => setShowAddTopic(false)}
                    className="btn btn-secondary"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleAddTopic}
                    className="btn btn-primary"
                  >
                    Crear
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="topics-list">
          {topics.map((topic) => (
            <div key={topic.id} className="topic-card">
              <div className="topic-content">
                <div className="topic-header">
                  <div style={{ flex: 1 }}>
                    {editingTopic?.id === topic.id ? (
                      <div className="space-y-3">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="form-input"
                        />
                        <textarea
                          value={editDesc}
                          onChange={(e) => setEditDesc(e.target.value)}
                          rows="2"
                          className="form-input"
                        />
                        <div className="flex gap-2">
                          <button 
                            onClick={handleUpdateTopic} 
                            className="btn btn-success"
                          >
                            <Save size={16} /> Guardar
                          </button>
                          <button
                            onClick={() => setEditingTopic(null)}
                            className="btn btn-secondary"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <h2 className="topic-title">{topic.title}</h2>
                        <p className="topic-description">{topic.description}</p>
                      </>
                    )}
                  </div>
                  
                  {!editingTopic && (
                    <div className="flex items-center gap-3 ml-4">
                      <button
                        onClick={() => handleVoteTopic(topic.id)}
                        className="vote-count"
                      >
                        <ThumbsUp size={18} />
                        <span>{topic.votes}</span>
                      </button>
                      <button
                        onClick={() => startEditTopic(topic)}
                        className="btn btn-secondary"
                        style={{ padding: '0.5rem' }}
                      >
                        <Edit2 size={20} />
                      </button>
                      <button
                        onClick={() => handleDeleteTopic(topic.id)}
                        className="btn btn-danger"
                        style={{ padding: '0.5rem' }}
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  )}
                </div>

                <div className="links-section">
                  <div className="links-header">
                    <h3 className="links-title">
                      <Link2 size={18} />
                      Enlaces útiles
                    </h3>
                    <button
                      onClick={() => setAddingLinkTo(topic.id)}
                      className="btn btn-success"
                      style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
                    >
                      <Plus size={16} /> Agregar enlace
                    </button>
                  </div>

                  {addingLinkTo === topic.id && (
                    <div style={{ backgroundColor: '#f9fafb', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                        <input
                          type="text"
                          value={newLinkTitle}
                          onChange={(e) => setNewLinkTitle(e.target.value)}
                          placeholder="Título del enlace"
                          className="form-input"
                        />
                        <input
                          type="url"
                          value={newLinkUrl}
                          onChange={(e) => setNewLinkUrl(e.target.value)}
                          placeholder="https://..."
                          className="form-input"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button onClick={handleAddLink} className="btn btn-success">
                          Agregar
                        </button>
                        <button
                          onClick={() => setAddingLinkTo(null)}
                          className="btn btn-secondary"
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="links-list">
                    {topic.links.sort((a, b) => b.votes - a.votes).map((link) => (
                      <div key={link.id} className="link-item">
                        {editingLink?.id === link.id && editingLink?.topicId === topic.id ? (
                          <div style={{ display: 'flex', gap: '0.5rem', width: '100%' }}>
                            <input
                              type="text"
                              value={editLinkTitle}
                              onChange={(e) => setEditLinkTitle(e.target.value)}
                              className="form-input"
                              style={{ flex: 1 }}
                            />
                            <input
                              type="url"
                              value={editLinkUrl}
                              onChange={(e) => setEditLinkUrl(e.target.value)}
                              className="form-input"
                              style={{ flex: 1 }}
                            />
                            <button 
                              onClick={handleUpdateLink} 
                              className="btn btn-success"
                              style={{ padding: '0.5rem' }}
                            >
                              <Save size={16} />
                            </button>
                            <button
                              onClick={() => setEditingLink(null)}
                              className="btn btn-secondary"
                              style={{ padding: '0.5rem' }}
                            >
                              <X size={16} />
                            </button>
                          </div>
                        ) : (
                          <>
                            <a
                              href={link.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ flex: 1, color: '#2563eb', textDecoration: 'none' }}
                              onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                              onMouseOut={(e) => e.target.style.textDecoration = 'none'}
                            >
                              {link.title}
                            </a>
                            <div className="link-actions">
                              <button
                                onClick={() => handleVoteLink(topic.id, link.id)}
                                className="link-vote-count"
                              >
                                <ThumbsUp size={14} />
                                <span>{link.votes}</span>
                              </button>
                              <button
                                onClick={() => startEditLink(link, topic.id)}
                                className="btn btn-secondary"
                                style={{ padding: '0.25rem' }}
                              >
                                <Edit2 size={16} />
                              </button>
                              <button
                                onClick={() => handleDeleteLink(topic.id, link.id)}
                                className="btn btn-danger"
                                style={{ padding: '0.25rem' }}
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    ))}
                    {topic.links.length === 0 && (
                      <p className="text-sm italic" style={{ color: '#6b7280' }}>No hay enlaces aún</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {topics.length === 0 && (
          <div className="text-center" style={{ padding: '3rem 0' }}>
            <p style={{ color: '#6b7280', fontSize: '1.25rem' }}>No hay temas todavía. ¡Crea el primero!</p>
          </div>
        )}
      </div>
    </div>
  );
}