from flask import Blueprint, render_template, flash, redirect, url_for, send_from_directory, request, current_app
from newblog.forms import PostForm, CategoryForm
from flask_login import current_user, login_required
from newblog.models import Post, Category, db, Comment
from newblog.decorators import editor_required, admin_required
from newblog.utils import redirect_back, random_filename
from flask_ckeditor import upload_fail, upload_success
from newblog.extensions import csrf
import os

editor = Blueprint('editor', __name__)


@editor.route('/files/<filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


@csrf.exempt
@editor.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.filename = random_filename(f.filename)
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
    url = url_for('.uploaded_files', filename=f.filename)
    return upload_success(url=url)


@editor.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@editor_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if not current_user.is_administrator():
        if current_user.id != post.author.id:
            return redirect_back()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()

        flash('Post updated.', 'success')
        return redirect(url_for('main.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('editor/edit_post.html', form=form)


@editor.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_administrator():
        if current_user.id != post.author.id:
            return redirect_back()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()


@editor.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('main.show_post', post_id=comment.post.id))
    return redirect(
        url_for('main.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')


@editor.route('/comment/<int:comment_id>/delete', methods=['POST'])
@editor_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not current_user.is_administrator():
        if current_user.id != comment.post.author.id:
            return redirect_back()
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@editor.route('/comment/<int:comment_id>/review', methods=['POST'])
@editor_required
def review_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not current_user.is_administrator():
        if current_user.id != comment.post.author.id:
            flash('Permission denied.', 'success')
            return redirect_back()
    comment.reviewed = True
    db.session.add(comment)
    db.session.commit()

    flash('Review deleted.', 'success')
    return redirect_back()


@editor.route('/new_post', methods=['GET', 'POST'])
@editor_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(author=current_user, title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()

        flash('Post created.', 'success')
        return redirect(url_for('main.show_post', post_id=post.id))
    return render_template('editor/new_post.html', form=form)


@editor.route('/comment/manage')
@login_required
def manage_comment():
    filter_rule = request.args.get('filter', 'all')  # 'all', 'unreviewed', 'admin'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['NEWBLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.join(Post, Post.id == Comment.post_id).filter(
            Post.author_id == current_user.id, Comment.reviewed == False)
    else:

        filtered_comments = Comment.query.join(Post, Post.id == Comment.post_id).filter(
            Post.author_id == current_user.id)

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('editor/manage_comment.html', comments=comments, pagination=pagination)


@editor.route('/category/new', methods=['GET', 'POST'])
@editor_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        if Category.query.filter_by(name=name).first():
            flash('已有同名分类')
            return redirect(url_for('main.index'))
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()

        flash('Category created.', 'success')
        return redirect(url_for('main.index'))
    return render_template('editor/new_category.html', form=form)


@editor.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_administrator():
        if current_user.id != post.author.id:
            return redirect_back()
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()

    return redirect_back()


@editor.route('/category/<int:category_id>/delete', methods=['POST'])
@editor_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('main.index'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('.manage_category'))
